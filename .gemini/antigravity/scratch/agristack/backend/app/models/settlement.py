import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class SettlementStatus(str, Enum):
    PROCESSING = "PROCESSING"
    CALCULATED = "CALCULATED"
    DISBURSING = "DISBURSING"
    COMPLETED = "COMPLETED"

class Settlement(Base, TimestampMixin):
    __tablename__ = "settlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False)
    initiated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Financial Statement
    gross_revenue_inr = Column(Numeric(12, 2), nullable=True)
    actual_expenses_inr = Column(Numeric(12, 2), nullable=True)
    platform_fee_inr = Column(Numeric(12, 2), nullable=True)  # 5% platform fee
    insurance_recovered_inr = Column(Numeric(12, 2), default=0.00, nullable=True)
    
    gross_revenue = Column(Numeric(12, 2), nullable=True)
    total_expenses = Column(Numeric(12, 2), nullable=True)
    platform_fee = Column(Numeric(12, 2), nullable=True)
    insurance_recovered = Column(Numeric(12, 2), default=0.00, nullable=True)

    # Bottom-line distribution
    net_distributable_inr = Column(Numeric(12, 2), nullable=True)
    net_distributable = Column(Numeric(12, 2), nullable=True)
    is_profit = Column(Boolean, default=True, nullable=False)
    per_share_return_inr = Column(Numeric(10, 2), default=0.00, nullable=False)
    total_investor_shares = Column(Integer, default=0, nullable=True)
    
    status = Column(String(50), default=SettlementStatus.COMPLETED.value, nullable=False)
    notes = Column(Text, nullable=True)
    settled_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="settlement")
    payouts = relationship("InvestorPayout", back_populates="settlement", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if "gross_revenue" in kwargs and "gross_revenue_inr" not in kwargs:
            kwargs["gross_revenue_inr"] = kwargs["gross_revenue"]
        elif "gross_revenue_inr" in kwargs and "gross_revenue" not in kwargs:
            kwargs["gross_revenue"] = kwargs["gross_revenue_inr"]

        if "total_expenses" in kwargs and "actual_expenses_inr" not in kwargs:
            kwargs["actual_expenses_inr"] = kwargs["total_expenses"]
        elif "actual_expenses_inr" in kwargs and "total_expenses" not in kwargs:
            kwargs["total_expenses"] = kwargs["actual_expenses_inr"]

        if "platform_fee" in kwargs and "platform_fee_inr" not in kwargs:
            kwargs["platform_fee_inr"] = kwargs["platform_fee"]
        elif "platform_fee_inr" in kwargs and "platform_fee" not in kwargs:
            kwargs["platform_fee"] = kwargs["platform_fee_inr"]

        if "insurance_recovered" in kwargs and "insurance_recovered_inr" not in kwargs:
            kwargs["insurance_recovered_inr"] = kwargs["insurance_recovered"]
        elif "insurance_recovered_inr" in kwargs and "insurance_recovered" not in kwargs:
            kwargs["insurance_recovered"] = kwargs["insurance_recovered_inr"]

        if "net_distributable" in kwargs and "net_distributable_inr" not in kwargs:
            kwargs["net_distributable_inr"] = kwargs["net_distributable"]
        elif "net_distributable_inr" in kwargs and "net_distributable" not in kwargs:
            kwargs["net_distributable"] = kwargs["net_distributable_inr"]

        if "is_profit" not in kwargs and "net_distributable" in kwargs:
            kwargs["is_profit"] = kwargs["net_distributable"] >= 0

        super().__init__(**kwargs)

class InvestorPayout(Base, TimestampMixin):
    __tablename__ = "investor_payouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    settlement_id = Column(UUID(as_uuid=True), ForeignKey("settlements.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    investor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    shares_held = Column(Integer, default=0, nullable=False)
    payout_amount_inr = Column(Numeric(12, 2), nullable=True)
    payout_amount = Column(Numeric(12, 2), nullable=True)
    bank_ref_number = Column(String(100), nullable=True)
    transfer_reference = Column(String(100), nullable=True)
    transferred_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="INITIATED", nullable=False)

    settlement = relationship("Settlement", back_populates="payouts")
    user = relationship("User", foreign_keys=[user_id])

    def __init__(self, **kwargs):
        if "investor_id" in kwargs and "user_id" not in kwargs:
            kwargs["user_id"] = kwargs["investor_id"]
        elif "user_id" in kwargs and "investor_id" not in kwargs:
            kwargs["investor_id"] = kwargs["user_id"]

        if "payout_amount" in kwargs and "payout_amount_inr" not in kwargs:
            kwargs["payout_amount_inr"] = kwargs["payout_amount"]
        elif "payout_amount_inr" in kwargs and "payout_amount" not in kwargs:
            kwargs["payout_amount"] = kwargs["payout_amount_inr"]

        super().__init__(**kwargs)
