"""
Disputes router — crop failure claims + general disputes.
"""
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.dispute import (
    CropFailureClaimRequest,
    CropFailureClaimOut,
    ReviewClaimRequest,
    DisputeRequest,
    DisputeOut,
    ResolveDisputeRequest,
)
from app.services.dispute_service import DisputeService

router = APIRouter(prefix="/disputes", tags=["Disputes"])


# ─── Crop Failure Claims ────────────────────────────────────────────────────

@router.post(
    "/crop-failure",
    response_model=CropFailureClaimOut,
    status_code=status.HTTP_201_CREATED,
    summary="Farmer submits a crop failure / insurance claim",
)
def submit_crop_failure(
    body: CropFailureClaimRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["FARMER"])),
):
    return DisputeService.submit_crop_failure_claim(
        db=db,
        farmer=current_user,
        project_id=body.project_id,
        failure_reason=body.failure_reason,
        affected_area_pct=body.affected_area_pct,
        evidence_urls=body.evidence_urls,
        insurance_policy_number=body.insurance_policy_number,
    )


@router.get(
    "/crop-failure/pending",
    response_model=List[CropFailureClaimOut],
    summary="Admin: list all pending crop failure claims",
)
def pending_claims(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"])),
):
    return DisputeService.list_pending_claims(db=db)


@router.patch(
    "/crop-failure/{claim_id}/review",
    response_model=CropFailureClaimOut,
    summary="Admin reviews (approves/rejects) a crop failure claim",
)
def review_claim(
    claim_id: UUID,
    body: ReviewClaimRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"])),
):
    return DisputeService.review_crop_failure_claim(
        db=db,
        admin=current_user,
        claim_id=claim_id,
        decision=body.decision,
        insurance_approved_amount=body.insurance_approved_amount,
        admin_notes=body.admin_notes,
    )


# ─── General Disputes ───────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=DisputeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Raise a general dispute on a project",
)
def raise_dispute(
    body: DisputeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DisputeService.raise_dispute(
        db=db,
        requester=current_user,
        project_id=body.project_id,
        dispute_type=body.dispute_type,
        description=body.description,
        evidence_urls=body.evidence_urls,
    )


@router.get(
    "/open",
    response_model=List[DisputeOut],
    summary="Admin: list all open / under-review disputes",
)
def open_disputes(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"])),
):
    return DisputeService.list_open_disputes(db=db)


@router.patch(
    "/{dispute_id}/resolve",
    response_model=DisputeOut,
    summary="Admin resolves a dispute",
)
def resolve_dispute(
    dispute_id: UUID,
    body: ResolveDisputeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"])),
):
    return DisputeService.resolve_dispute(
        db=db,
        admin=current_user,
        dispute_id=dispute_id,
        resolution=body.resolution,
        resolution_notes=body.resolution_notes,
    )
