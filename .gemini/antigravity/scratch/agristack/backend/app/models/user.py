import uuid
from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class UserRole(str, Enum):
    FARMER = "FARMER"
    INVESTOR = "INVESTOR"
    ADMIN = "ADMIN"
    GOV_OFFICER = "GOV_OFFICER"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    primary_role = Column(String(50), default=UserRole.FARMER.value, nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Multi-Factor Authentication
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255), nullable=True)  # Encrypted TOTP secret
    
    # Regional preferences
    preferred_language = Column(String(10), default="en", nullable=False)  # en, hi, mr
    
    # Relationships
    kyc_record = relationship("KYCRecord", back_populates="user", uselist=False, cascade="all, delete-orphan", foreign_keys="KYCRecord.user_id")
    farms = relationship("Farm", back_populates="farmer", cascade="all, delete-orphan")
    share_holdings = relationship("ShareHolding", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="investor", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="actor")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")
