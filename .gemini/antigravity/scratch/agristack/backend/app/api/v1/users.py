from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User
from ...models.compliance import ComplianceConsent
from ...schemas.user import UserResponse, UserUpdate
from ...schemas.audit import ComplianceConsentRequest, ComplianceConsentResponse
from ...services.audit_service import AuditService

router = APIRouter(prefix="/users", tags=["Users & Compliance Consents"])

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user profile."""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_profile(req: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Updates user personal preferences."""
    if req.full_name is not None:
        current_user.full_name = req.full_name
    if req.preferred_language is not None:
        current_user.preferred_language = req.preferred_language
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/consent", response_model=ComplianceConsentResponse)
def record_compliance_consent(
    req: ComplianceConsentRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Records statutory consent for SEBI CIS Sandbox Pilot terms,
    DigiLocker document pulls, or platform Terms of Service.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    consent = ComplianceConsent(
        user_id=current_user.id,
        consent_type=req.consent_type,
        version=req.version,
        ip_address=client_ip
    )
    db.add(consent)
    db.commit()
    db.refresh(consent)

    AuditService.log_action(
        db=db,
        action="COMPLIANCE_CONSENT_SIGNED",
        resource_type="CONSENT",
        resource_id=str(consent.id),
        actor_role=current_user.primary_role,
        actor_id=current_user.id,
        ip_address=client_ip,
        details={"consent_type": req.consent_type, "version": req.version}
    )

    return consent

@router.get("/export-data")
def export_user_data(current_user: User = Depends(get_current_user)):
    """Data portability endpoint complying with DPDP Act data rights."""
    return {
        "user_profile": {
            "id": str(current_user.id),
            "email": current_user.email,
            "phone_number": current_user.phone_number,
            "full_name": current_user.full_name,
            "role": current_user.primary_role,
            "language": current_user.preferred_language,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        },
        "privacy_notice": "Personal data export generated in accordance with Digital Personal Data Protection guidelines."
    }
