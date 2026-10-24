import uuid
from enum import Enum
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class PaymentStatus(str, Enum):
    INITIATED = "INITIATED"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class PaymentTransaction(Base, TimestampMixin):
    __tablename__ = "payment_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    
    razorpay_order_id = Column(String(100), unique=True, nullable=False, index=True)
    razorpay_payment_id = Column(String(100), unique=True, nullable=True, index=True)
    razorpay_signature = Column(String(255), nullable=True)
    
    # Idempotency key to prevent double charging
    idempotency_key = Column(String(128), unique=True, nullable=False, index=True)
    
    amount_inr = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    status = Column(String(50), default=PaymentStatus.INITIATED.value, nullable=False)
    
    webhook_verified = Column(Boolean, default=False, nullable=False)
    gateway_payload = Column(JSON, nullable=True)

    user = relationship("User")
