import uuid
from enum import Enum
from sqlalchemy import Column, String, Numeric, Integer, Boolean, ForeignKey
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class HoldingType(str, Enum):
    FARMER_EQUITY = "FARMER_EQUITY"
    INVESTOR_PURCHASE = "INVESTOR_PURCHASE"

class ShareHolding(Base, TimestampMixin):
    __tablename__ = "share_holdings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    share_count = Column(Integer, default=0, nullable=False)
    share_percentage = Column(Numeric(5, 2), default=0.00, nullable=False)
    total_invested_amount_inr = Column(Numeric(12, 2), default=0.00, nullable=False)
    holding_type = Column(String(50), default=HoldingType.INVESTOR_PURCHASE.value, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="share_holdings")
    project = relationship("Project", back_populates="share_holdings")
