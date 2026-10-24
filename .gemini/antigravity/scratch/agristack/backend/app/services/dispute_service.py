"""
Dispute service — crop failure claims, insurance, and general disputes.
All disputes enter Admin review queue; resolution audit-logged.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.dispute import CropFailureClaim, DisputeRecord
from app.models.project import Project
from app.models.user import User
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class DisputeService:
    # -----------------------------------------------------------------------
    # Crop Failure Claims
    # -----------------------------------------------------------------------

    @staticmethod
    def submit_crop_failure_claim(
        db: Session,
        farmer: User,
        project_id: UUID,
        failure_reason: str,
        affected_area_pct: float,
        evidence_urls: Optional[List[str]] = None,
        insurance_policy_number: Optional[str] = None,
    ) -> CropFailureClaim:
        """Farmer submits a crop failure claim — enters admin review queue."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundError("Project not found")
        if project.farmer_id != farmer.id:
            raise ForbiddenError("Only the project farmer can submit a failure claim")
        if project.status not in ("IN_PROGRESS", "HARVESTED"):
            raise ValidationError(
                f"Crop failure claim requires IN_PROGRESS/HARVESTED project (current: {project.status})"
            )

        claim = CropFailureClaim(
            project_id=project_id,
            farmer_id=farmer.id,
            failure_reason=failure_reason,
            affected_area_pct=affected_area_pct,
            evidence_urls=evidence_urls or [],
            insurance_policy_number=insurance_policy_number,
            status="PENDING",
        )
        db.add(claim)

        # Flag the project for admin attention
        if project.status == "IN_PROGRESS":
            project.status = "FLAGGED"

        db.commit()
        db.refresh(claim)

        AuditService.log_action(
            db=db,
            actor_id=farmer.id,
            action="CROP_FAILURE_CLAIM_SUBMITTED",
            resource_type="crop_failure_claim",
            resource_id=str(claim.id),
            details={
                "project_id": str(project_id),
                "failure_reason": failure_reason,
                "affected_area_pct": affected_area_pct,
            },
        )
        return claim

    @staticmethod
    def review_crop_failure_claim(
        db: Session,
        admin: User,
        claim_id: UUID,
        decision: str,  # APPROVED | REJECTED
        insurance_approved_amount: Optional[float] = None,
        admin_notes: Optional[str] = None,
    ) -> CropFailureClaim:
        if decision not in ("APPROVED", "REJECTED"):
            raise ValidationError("Decision must be APPROVED or REJECTED")

        claim = db.query(CropFailureClaim).filter(CropFailureClaim.id == claim_id).first()
        if not claim:
            raise NotFoundError("Claim not found")
        if claim.status != "PENDING":
            raise ValidationError(f"Claim is already {claim.status}")

        claim.status = decision
        claim.reviewed_by = admin.id
        claim.reviewed_at = datetime.now(timezone.utc)
        claim.admin_notes = admin_notes
        if decision == "APPROVED" and insurance_approved_amount:
            claim.insurance_approved_amount = insurance_approved_amount

        db.commit()
        db.refresh(claim)

        AuditService.log_action(
            db=db,
            actor_id=admin.id,
            action=f"CROP_FAILURE_CLAIM_{decision}",
            resource_type="crop_failure_claim",
            resource_id=str(claim.id),
            details={"insurance_amount": insurance_approved_amount, "notes": admin_notes},
        )
        return claim

    @staticmethod
    def list_pending_claims(db: Session) -> List[CropFailureClaim]:
        return (
            db.query(CropFailureClaim)
            .filter(CropFailureClaim.status == "PENDING")
            .order_by(CropFailureClaim.created_at)
            .all()
        )

    # -----------------------------------------------------------------------
    # General Disputes
    # -----------------------------------------------------------------------

    @staticmethod
    def raise_dispute(
        db: Session,
        requester: User,
        project_id: UUID,
        dispute_type: str,
        description: str,
        evidence_urls: Optional[List[str]] = None,
    ) -> DisputeRecord:
        """Any platform participant can raise a dispute on a project."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundError("Project not found")

        dispute = DisputeRecord(
            project_id=project_id,
            raised_by=requester.id,
            dispute_type=dispute_type,
            description=description,
            evidence_urls=evidence_urls or [],
            status="OPEN",
        )
        db.add(dispute)
        db.commit()
        db.refresh(dispute)

        AuditService.log_action(
            db=db,
            actor_id=requester.id,
            action="DISPUTE_RAISED",
            resource_type="dispute_record",
            resource_id=str(dispute.id),
            details={"type": dispute_type, "project_id": str(project_id)},
        )
        return dispute

    @staticmethod
    def resolve_dispute(
        db: Session,
        admin: User,
        dispute_id: UUID,
        resolution: str,
        resolution_notes: Optional[str] = None,
    ) -> DisputeRecord:
        dispute = db.query(DisputeRecord).filter(DisputeRecord.id == dispute_id).first()
        if not dispute:
            raise NotFoundError("Dispute not found")
        if dispute.status not in ("OPEN", "UNDER_REVIEW"):
            raise ValidationError(f"Dispute is already {dispute.status}")

        dispute.status = "RESOLVED"
        dispute.resolution = resolution
        dispute.resolution_notes = resolution_notes
        dispute.resolved_by = admin.id
        dispute.resolved_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(dispute)

        AuditService.log_action(
            db=db,
            actor_id=admin.id,
            action="DISPUTE_RESOLVED",
            resource_type="dispute_record",
            resource_id=str(dispute.id),
            details={"resolution": resolution},
        )
        return dispute

    @staticmethod
    def list_open_disputes(db: Session) -> List[DisputeRecord]:
        return (
            db.query(DisputeRecord)
            .filter(DisputeRecord.status.in_(("OPEN", "UNDER_REVIEW")))
            .order_by(DisputeRecord.created_at)
            .all()
        )
