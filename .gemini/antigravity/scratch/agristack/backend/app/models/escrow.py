import uuid
from enum import Enum
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class EscrowStatus(str, Enum):
    LOCKED = "LOCKED"
    SUBMITTED = "SUBMITTED"
    VERIFIED = "VERIFIED"
    RELEASED = "RELEASED"
    DISPUTED = "DISPUTED"

class EscrowMilestone(Base, TimestampMixin):
    __tablename__ = "escrow_milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    milestone_index = Column(Integer, nullable=False)  # 1: Sowing (40%), 2: Mid-cycle (40%), 3: Harvest (20%)
    name = Column(String(100), nullable=False)
    percentage_release = Column(Numeric(5, 2), nullable=False)
    amount_inr = Column(Numeric(12, 2), nullable=False)
    
    status = Column(String(50), default=EscrowStatus.LOCKED.value, nullable=False)
    proof_document_url = Column(String(512), nullable=True)
    verified_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    verification_notes = Column(Text, nullable=True)
    released_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="escrow_milestones")

class Investment(Base, TimestampMixin):
    __tablename__ = "investments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    share_count = Column(Integer, nullable=False)
    total_amount_inr = Column(Numeric(12, 2), nullable=False)
    
    agreement_signed = Column(Boolean, default=False, nullable=False)
    agreement_pdf_url = Column(String(512), nullable=True)
    payment_transaction_id = Column(UUID(as_uuid=True), ForeignKey("payment_transactions.id"), nullable=True)
    escrow_status = Column(String(50), default="HELD_IN_ESCROW", nullable=False)
    status = Column(String(50), default="CONFIRMED", nullable=False)

    investor = relationship("User", back_populates="investments")
    project = relationship("Project", back_populates="investments")
    payment = relationship("PaymentTransaction")
