"""
Settlements router — initiate distribution, payout tracking.
"""
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.settlement import (
    InitiateSettlementRequest,
    SettlementOut,
    PayoutOut,
    MarkTransferRequest,
)
from app.services.settlement_service import SettlementService

router = APIRouter(prefix="/settlements", tags=["Settlements"])


@router.post(
    "/",
    response_model=SettlementOut,
    status_code=status.HTTP_201_CREATED,
    summary="Admin initiates pro-rata settlement for a project",
)
def initiate_settlement(
    body: InitiateSettlementRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"])),
):
    return SettlementService.initiate_settlement(
        db=db,
        admin=current_user,
        project_id=body.project_id,
        gross_revenue=body.gross_revenue,
        total_expenses=body.total_expenses,
        insurance_recovered=body.insurance_recovered,
        notes=body.notes,
    )


@router.get(
    "/project/{project_id}",
    response_model=SettlementOut,
    summary="Get settlement details for a project",
)
def get_settlement(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    s = SettlementService.get_settlement(db=db, project_id=project_id)
    if not s:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No settlement found for this project")
    return s


@router.get(
    "/my-payouts",
    response_model=List[PayoutOut],
    summary="List all payouts for the authenticated investor",
)
def my_payouts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["INVESTOR", "FARMER", "ADMIN"])),
):
    return SettlementService.get_payouts_for_investor(db=db, investor_id=current_user.id)


@router.patch(
    "/payouts/{payout_id}/transfer",
    response_model=PayoutOut,
    summary="Admin marks a payout as transferred",
)
def mark_transferred(
    payout_id: UUID,
    body: MarkTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"])),
):
    return SettlementService.mark_payout_transferred(
        db=db,
        payout_id=payout_id,
        admin=current_user,
        transfer_reference=body.transfer_reference,
    )
