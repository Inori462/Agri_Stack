import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.kyc import KYCRecord, KYCStatus
from ..models.user import User
from ..core.security import mask_aadhaar, hash_aadhaar, encrypt_pii
from ..core.exceptions import DuplicateResourceError, EntityNotFoundError, AppException
from ..adapters.digilocker_adapter import DigiLockerAdapter
from ..services.audit_service import AuditService

class KYCService:
    """Service handling multi-step farmer onboarding KYC and land document verifications."""

    @staticmethod
    def submit_kyc(
        db: Session,
        user: User,
        raw_aadhaar: str,
        pan_number: Optional[str] = None,
        satbara_document_url: Optional[str] = None,
        survey_number_claimed: Optional[str] = None,
        ip_address: str = "127.0.0.1"
    ) -> KYCRecord:
        """
        Submits or updates user's KYC record with strict Aadhaar data minimization.
        Enforces duplicate detection via server-peppered HMAC-SHA256 hash.
        """
        aadhaar_hash = hash_aadhaar(raw_aadhaar)
        aadhaar_last4 = mask_aadhaar(raw_aadhaar)[-4:]

        # Check if another user already registered this Aadhaar identity
        existing_with_hash = (
            db.query(KYCRecord)
            .filter(KYCRecord.aadhaar_hash == aadhaar_hash, KYCRecord.user_id != user.id)
            .first()
        )
        if existing_with_hash:
            AuditService.record_security_alert(
                db=db,
                alert_type="DUPLICATE_AADHAAR_SUBMITTED",
                severity="HIGH",
                details={"user_id": str(user.id), "existing_user_id": str(existing_with_hash.user_id)}
            )
            raise DuplicateResourceError("This Aadhaar identity is already registered under another account")

        # Mask/Encrypt PAN if provided
        pan_masked = None
        if pan_number:
            pan_info = DigiLockerAdapter.pull_pan_profile(pan_number)
            pan_masked = pan_info.get("pan")

        # Fetch existing record or create new
        kyc = db.query(KYCRecord).filter(KYCRecord.user_id == user.id).first()
        if not kyc:
            kyc = KYCRecord(
                user_id=user.id,
                aadhaar_last4=aadhaar_last4,
                aadhaar_hash=aadhaar_hash,
                pan_masked=pan_masked,
                satbara_document_url=satbara_document_url,
                survey_number_claimed=survey_number_claimed,
                verification_status=KYCStatus.SUBMITTED.value
            )
            db.add(kyc)
        else:
            kyc.aadhaar_last4 = aadhaar_last4
            kyc.aadhaar_hash = aadhaar_hash
            kyc.pan_masked = pan_masked
            kyc.satbara_document_url = satbara_document_url
            kyc.survey_number_claimed = survey_number_claimed
            kyc.verification_status = KYCStatus.SUBMITTED.value

        db.commit()
        db.refresh(kyc)

        AuditService.log_action(
            db=db,
            action="KYC_SUBMISSION",
            resource_type="KYC",
            resource_id=str(kyc.id),
            actor_role=user.primary_role,
            actor_id=user.id,
            ip_address=ip_address,
            details={"aadhaar_last4": aadhaar_last4, "survey_number": survey_number_claimed}
        )

        return kyc

    @staticmethod
    def pull_digilocker_kyc(db: Session, user: User, access_token: str = "mock_token") -> KYCRecord:
        """One-click DigiLocker e-KYC pull."""
        profile = DigiLockerAdapter.pull_aadhaar_profile(access_token)
        aadhaar_last4 = profile["masked_aadhaar"][-4:]
        aadhaar_hash = hash_aadhaar("12345678" + aadhaar_last4)

        kyc = db.query(KYCRecord).filter(KYCRecord.user_id == user.id).first()
        if not kyc:
            kyc = KYCRecord(
                user_id=user.id,
                aadhaar_last4=aadhaar_last4,
                aadhaar_hash=aadhaar_hash,
                digilocker_uri=profile["digilocker_doc_uri"],
                verification_status=KYCStatus.AUTO_VERIFIED.value,
                verified_at=datetime.now(timezone.utc)
            )
            db.add(kyc)
        else:
            kyc.aadhaar_last4 = aadhaar_last4
            kyc.aadhaar_hash = aadhaar_hash
            kyc.digilocker_uri = profile["digilocker_doc_uri"]
            kyc.verification_status = KYCStatus.AUTO_VERIFIED.value
            kyc.verified_at = datetime.now(timezone.utc)

        user.is_verified = True
        db.commit()
        db.refresh(kyc)
        return kyc

    @staticmethod
    def admin_review(
        db: Session,
        kyc_id: uuid.UUID,
        admin_user: User,
        decision: str,
        rejection_reason: Optional[str] = None
    ) -> KYCRecord:
        """Admin review for manual KYC verification queue."""
        kyc = db.query(KYCRecord).filter(KYCRecord.id == kyc_id).first()
        if not kyc:
            raise EntityNotFoundError("KYC record not found")

        decision_upper = decision.upper()
        if decision_upper not in {KYCStatus.VERIFIED.value, KYCStatus.REJECTED.value}:
            raise AppException("Decision must be either 'VERIFIED' or 'REJECTED'")

        kyc.verification_status = decision_upper
        kyc.verified_by_admin_id = admin_user.id
        kyc.rejection_reason = rejection_reason if decision_upper == KYCStatus.REJECTED.value else None
        kyc.verified_at = datetime.now(timezone.utc)

        # Update user.is_verified status
        target_user = db.query(User).filter(User.id == kyc.user_id).first()
        if target_user:
            target_user.is_verified = (decision_upper == KYCStatus.VERIFIED.value)

        db.commit()
        db.refresh(kyc)

        AuditService.log_action(
            db=db,
            action="KYC_ADMIN_DECISION",
            resource_type="KYC",
            resource_id=str(kyc.id),
            actor_role=admin_user.primary_role,
            actor_id=admin_user.id,
            details={"decision": decision_upper, "target_user_id": str(kyc.user_id)}
        )

        return kyc
