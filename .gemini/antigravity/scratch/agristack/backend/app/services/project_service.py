import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models.project import Project, ProjectStatus, ProjectStateLog
from ..models.farm import Farm, LandParcel
from ..models.user import User, UserRole
from ..models.escrow import EscrowMilestone, EscrowStatus
from ..models.share import ShareHolding, HoldingType
from ..models.ledger import LedgerTransactionType
from ..schemas.project import ProjectCreate
from ..core.state_machine import validate_state_transition
from ..core.exceptions import EntityNotFoundError, PermissionDeniedError, AppException
from ..services.ledger_service import LedgerService
from ..services.audit_service import AuditService

class ProjectService:
    """Service governing crop cycle projects, milestone escrow, and fractional digital shares."""

    @staticmethod
    def create_project(db: Session, farmer: User, data: ProjectCreate) -> Project:
        """
        Creates a new crop cycle enterprise project, initial milestone tiers,
        and farmer genesis digital equity shares with SHA-256 hash chaining.
        """
        # Validate farm ownership
        farm = db.query(Farm).filter(Farm.id == data.farm_id).first()
        if not farm:
            raise EntityNotFoundError("Farm not found")
        if farm.farmer_id != farmer.id and farmer.primary_role != UserRole.ADMIN.value:
            raise PermissionDeniedError("You do not own this farm")

        parcel = db.query(LandParcel).filter(LandParcel.id == data.parcel_id, LandParcel.farm_id == farm.id).first()
        if not parcel:
            raise EntityNotFoundError("Land parcel not found under specified farm")

        # Digital share calculations
        total_shares = data.total_shares
        share_price_inr = round(data.total_valuation_inr / total_shares, 2)
        investor_pool_percent = round(100.0 - data.farmer_equity_percent, 2)
        farmer_shares_count = int(round(total_shares * (data.farmer_equity_percent / 100.0)))
        investor_target_funding = data.total_valuation_inr * (investor_pool_percent / 100.0)

        project = Project(
            farm_id=farm.id,
            parcel_id=parcel.id,
            farmer_id=farmer.id,
            title=data.title,
            crop_name=data.crop_name,
            crop_variety=data.crop_variety,
            season=data.season,
            sowing_date=data.sowing_date,
            estimated_harvest_date=data.estimated_harvest_date,
            status=ProjectStatus.DRAFT.value,
            total_valuation_inr=data.total_valuation_inr,
            farmer_equity_percent=data.farmer_equity_percent,
            investor_pool_percent=investor_pool_percent,
            total_shares=total_shares,
            share_price_inr=share_price_inr,
            funded_shares=0,
            expected_yield_quintals=data.expected_yield_quintals,
            expected_revenue_inr=data.expected_revenue_inr,
            risk_score=25  # Initial baseline
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        # 1. Initialize 3 Milestone Escrow tiers (40% Sowing, 40% Mid-cycle, 20% Harvest)
        milestones = [
            EscrowMilestone(
                project_id=project.id,
                milestone_index=1,
                name="Milestone 1: Sowing & Land Prep Verification (40%)",
                percentage_release=40.0,
                amount_inr=round(investor_target_funding * 0.40, 2),
                status=EscrowStatus.LOCKED.value
            ),
            EscrowMilestone(
                project_id=project.id,
                milestone_index=2,
                name="Milestone 2: Vegetative Growth & Satellite NDVI Monitoring (40%)",
                percentage_release=40.0,
                amount_inr=round(investor_target_funding * 0.40, 2),
                status=EscrowStatus.LOCKED.value
            ),
            EscrowMilestone(
                project_id=project.id,
                milestone_index=3,
                name="Milestone 3: Harvest Yield Verification (20%)",
                percentage_release=20.0,
                amount_inr=round(investor_target_funding * 0.20, 2),
                status=EscrowStatus.LOCKED.value
            ),
        ]
        db.add_all(milestones)

        # 2. Allocate Farmer Equity Shares
        farmer_holding = ShareHolding(
            user_id=farmer.id,
            project_id=project.id,
            share_count=farmer_shares_count,
            share_percentage=data.farmer_equity_percent,
            total_invested_amount_inr=round(farmer_shares_count * share_price_inr, 2),
            holding_type=HoldingType.FARMER_EQUITY.value
        )
        db.add(farmer_holding)
        db.commit()

        # 3. Cryptographic Ownership Ledger Genesis Issuance
        LedgerService.append_entry(
            db=db,
            project_id=project.id,
            transaction_type=LedgerTransactionType.GENESIS_ISSUANCE.value,
            to_user_id=farmer.id,
            shares_count=farmer_shares_count,
            price_per_share=share_price_inr,
            total_amount=round(farmer_shares_count * share_price_inr, 2),
            from_user_id=None
        )

        # 4. State log: DRAFT created
        state_log = ProjectStateLog(
            project_id=project.id,
            from_state="NONE",
            to_state=ProjectStatus.DRAFT.value,
            actor_id=farmer.id,
            rationale="Initial crop project creation"
        )
        db.add(state_log)
        db.commit()
        db.refresh(project)

        AuditService.log_action(
            db=db,
            action="PROJECT_CREATED",
            resource_type="PROJECT",
            resource_id=str(project.id),
            actor_role=farmer.primary_role,
            actor_id=farmer.id,
            details={
                "crop": project.crop_name,
                "valuation": float(project.total_valuation_inr),
                "farmer_shares": farmer_shares_count
            }
        )

        return project

    @staticmethod
    def transition_state(
        db: Session,
        project_id: uuid.UUID,
        next_state: str,
        actor: User,
        rationale: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Project:
        """
        Executes a validated state machine transition with strict RBAC rules.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise EntityNotFoundError("Project not found")

        current_state = project.status
        validate_state_transition(current_state, next_state)

        # Enforce RBAC on sensitive state transitions
        if next_state in [ProjectStatus.VERIFIED.value, ProjectStatus.REJECTED.value, ProjectStatus.FLAGGED.value]:
            if actor.primary_role != UserRole.ADMIN.value:
                raise PermissionDeniedError("Only platform administrators can verify, reject, or flag projects")

        if next_state == ProjectStatus.SUBMITTED.value:
            if actor.primary_role != UserRole.ADMIN.value and project.farmer_id != actor.id:
                raise PermissionDeniedError("Only the owning farmer can submit this project")

        # Update status
        project.status = next_state
        log_entry = ProjectStateLog(
            project_id=project.id,
            from_state=current_state,
            to_state=next_state,
            actor_id=actor.id,
            rationale=rationale,
            metadata_json=metadata
        )
        db.add(log_entry)
        db.commit()
        db.refresh(project)

        AuditService.log_action(
            db=db,
            action="PROJECT_STATE_TRANSITION",
            resource_type="PROJECT",
            resource_id=str(project.id),
            actor_role=actor.primary_role,
            actor_id=actor.id,
            details={"from": current_state, "to": next_state, "rationale": rationale}
        )

        return project

    @staticmethod
    def submit_milestone_proof(
        db: Session,
        project_id: uuid.UUID,
        milestone_index: int,
        farmer: User,
        proof_document_url: str,
        notes: Optional[str] = None
    ) -> EscrowMilestone:
        """Farmer submits verification evidence for a milestone."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise EntityNotFoundError("Project not found")
        if project.farmer_id != farmer.id and farmer.primary_role != UserRole.ADMIN.value:
            raise PermissionDeniedError("Only the project farmer can submit milestone proofs")

        milestone = (
            db.query(EscrowMilestone)
            .filter(EscrowMilestone.project_id == project_id, EscrowMilestone.milestone_index == milestone_index)
            .first()
        )
        if not milestone:
            raise EntityNotFoundError("Milestone not found")

        milestone.proof_document_url = proof_document_url
        milestone.verification_notes = notes
        milestone.status = EscrowStatus.SUBMITTED.value
        db.commit()
        db.refresh(milestone)
        return milestone

    @staticmethod
    def release_milestone_escrow(
        db: Session,
        milestone_id: uuid.UUID,
        admin_user: User,
        notes: Optional[str] = None
    ) -> EscrowMilestone:
        """
        Admin verifies milestone evidence and releases locked escrow funds to farmer.
        Appends cryptographic payout record in ownership ledger.
        """
        milestone = db.query(EscrowMilestone).filter(EscrowMilestone.id == milestone_id).first()
        if not milestone:
            raise EntityNotFoundError("Milestone not found")

        milestone.status = EscrowStatus.RELEASED.value
        milestone.verified_by_admin_id = admin_user.id
        milestone.released_at = datetime.now(timezone.utc)
        if notes:
            milestone.verification_notes = (milestone.verification_notes or "") + f" [Admin: {notes}]"

        project = milestone.project

        # If Milestone 1 (Sowing) is released and project is FUNDED, progress to IN_PROGRESS
        if milestone.milestone_index == 1 and project.status == ProjectStatus.FUNDED.value:
            project.status = ProjectStatus.IN_PROGRESS.value
            log = ProjectStateLog(
                project_id=project.id,
                from_state=ProjectStatus.FUNDED.value,
                to_state=ProjectStatus.IN_PROGRESS.value,
                actor_id=admin_user.id,
                rationale="Milestone 1 sowing verified: automatic progression to IN_PROGRESS"
            )
            db.add(log)

        db.commit()

        # Cryptographically record escrow payout in ownership ledger
        LedgerService.append_entry(
            db=db,
            project_id=project.id,
            transaction_type=LedgerTransactionType.ESCROW_PAYOUT.value,
            to_user_id=project.farmer_id,
            shares_count=0,
            price_per_share=0.0,
            total_amount=float(milestone.amount_inr),
            from_user_id=None
        )

        AuditService.log_action(
            db=db,
            action="ESCROW_MILESTONE_RELEASED",
            resource_type="ESCROW_MILESTONE",
            resource_id=str(milestone.id),
            actor_role=admin_user.primary_role,
            actor_id=admin_user.id,
            details={
                "milestone": milestone.name,
                "amount_inr": float(milestone.amount_inr),
                "project_id": str(project.id)
            }
        )

        db.refresh(milestone)
        return milestone
