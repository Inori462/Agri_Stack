import uuid
from enum import Enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class KYCStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    AUTO_VERIFIED = "AUTO_VERIFIED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class KYCRecord(Base, TimestampMixin):
    __tablename__ = "kyc_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Aadhaar privacy compliance (UIDAI guidelines): store only last 4 digits
    aadhaar_last4 = Column(String(4), nullable=False)
    # HMAC-SHA256 hash with secret pepper to detect duplicate identity without decrypting
    aadhaar_hash = Column(String(64), unique=True, nullable=False, index=True)
    
    pan_masked = Column(String(10), nullable=True)
    digilocker_uri = Column(String(255), nullable=True)
    
    # Maharashtra 7/12 (Satbara) Land Record document URL (S3)
    satbara_document_url = Column(String(512), nullable=True)
    survey_number_claimed = Column(String(100), nullable=True)
    
    verification_status = Column(String(50), default=KYCStatus.SUBMITTED.value, nullable=False)
    verified_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="kyc_record", foreign_keys=[user_id])
