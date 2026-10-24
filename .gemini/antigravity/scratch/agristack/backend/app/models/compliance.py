import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class ComplianceConsent(Base):
    __tablename__ = "compliance_consents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    consent_type = Column(String(100), nullable=False)  # SEBI_CIS_SANDBOX_ACK, TERMS_OF_SERVICE, DATA_PRIVACY
    version = Column(String(20), nullable=False)         # e.g., "1.0.0"
    ip_address = Column(String(45), nullable=False)
    agreed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User")

class TermsRecord(Base, TimestampMixin):
    __tablename__ = "terms_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    version = Column(String(20), unique=True, nullable=False)
    content_markdown = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
