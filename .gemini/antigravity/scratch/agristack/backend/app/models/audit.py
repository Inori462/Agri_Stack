from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    actor_role = Column(String(50), nullable=False)
    
    action = Column(String(100), nullable=False, index=True)  # LOGIN, KYC_DECISION, SHARE_TRANSFERRED, etc.
    resource_type = Column(String(100), nullable=False)        # PROJECT, USER, SHARE, PAYMENT
    resource_id = Column(String(100), nullable=False)
    
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(255), nullable=False)
    details = Column(JSON, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    actor = relationship("User", back_populates="audit_logs")

class SecurityAlert(Base):
    __tablename__ = "security_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(100), nullable=False)  # BRUTE_FORCE, TAMPER_DETECTED, DUPLICATE_SURVEY_NO
    severity = Column(String(20), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    details = Column(JSON, nullable=False)
    resolved = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
