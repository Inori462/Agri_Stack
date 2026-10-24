from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.dependencies import get_current_user, require_roles
from ...models.user import User, UserRole
from ...models.kyc import KYCRecord, KYCStatus
from ...schemas.kyc import KYCCreateRequest, KYCResponse, KYCApprovalRequest
from ...services.kyc_service import KYCService

router = APIRouter(prefix="/kyc", tags=["Farmer Onboarding & KYC"])

@router.post("/submit", response_model=KYCResponse, status_code=status.HTTP_200_OK)
def submit_kyc(
    req: KYCCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits identity details and Maharashtra 7/12 land document reference.
    Enforces Aadhaar data minimization and duplicate check.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    kyc = KYCService.submit_kyc(
        db=db,
        user=current_user,
        raw_aadhaar=req.aadhaar_number,
        pan_number=req.pan_number,
        satbara_document_url=req.satbara_document_url,
        survey_number_claimed=req.survey_number_claimed,
        ip_address=client_ip
    )
    return kyc

@router.get("/me", response_model=Optional[KYCResponse])
def get_my_kyc(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns KYC verification status for current user."""
    kyc = db.query(KYCRecord).filter(KYCRecord.user_id == current_user.id).first()
    return kyc

@router.post("/digilocker-pull", response_model=KYCResponse)
def digilocker_pull(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulates one-click DigiLocker identity and paperless verification."""
    kyc = KYCService.pull_digilocker_kyc(db=db, user=current_user)
    return kyc

@router.get("/admin/queue", response_model=List[KYCResponse])
def get_admin_kyc_queue(
    admin_user: User = Depends(require_roles([UserRole.ADMIN.value])),
    db: Session = Depends(get_db)
):
    """Admin queue: Lists all pending or submitted KYC records requiring review."""
    records = (
        db.query(KYCRecord)
        .filter(KYCRecord.verification_status.in_([KYCStatus.SUBMITTED.value, KYCStatus.MANUAL_REVIEW.value]))
        .order_by(KYCRecord.created_at.asc())
        .all()
    )
    return records

@router.post("/admin/{kyc_id}/decision", response_model=KYCResponse)
def admin_kyc_decision(
    kyc_id: UUID,
    req: KYCApprovalRequest,
    admin_user: User = Depends(require_roles([UserRole.ADMIN.value])),
    db: Session = Depends(get_db)
):
    """Admin action: Approves or rejects a farmer's KYC record with remarks."""
    kyc = KYCService.admin_review(
        db=db,
        kyc_id=kyc_id,
        admin_user=admin_user,
        decision=req.decision,
        rejection_reason=req.rejection_reason
    )
    return kyc
