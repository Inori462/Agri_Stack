from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class InvestorPayoutResponse(BaseModel):
    id: UUID
    settlement_id: UUID
    user_id: Optional[UUID] = None
    investor_id: Optional[UUID] = None
    shares_held: int
    payout_amount_inr: Optional[float] = None
    payout_amount: Optional[float] = None
    bank_ref_number: Optional[str] = None
    transfer_reference: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SettlementResponse(BaseModel):
    id: UUID
    project_id: UUID
    gross_revenue_inr: Optional[float] = None
    actual_expenses_inr: Optional[float] = None
    platform_fee_inr: Optional[float] = None
    insurance_recovered_inr: Optional[float] = 0.0
    net_distributable_inr: Optional[float] = None
    gross_revenue: Optional[float] = None
    total_expenses: Optional[float] = None
    platform_fee: Optional[float] = None
    insurance_recovered: Optional[float] = 0.0
    net_distributable: Optional[float] = None
    is_profit: Optional[bool] = True
    per_share_return_inr: Optional[float] = 0.0
    status: str
    settled_at: Optional[datetime] = None
    created_at: datetime
    payouts: List[InvestorPayoutResponse] = []

    model_config = ConfigDict(from_attributes=True)

# Phase 5 Settlements Router Schemas
class InitiateSettlementRequest(BaseModel):
    project_id: UUID
    gross_revenue: float = Field(..., gt=0)
    total_expenses: float = Field(..., ge=0)
    insurance_recovered: float = 0.0
    notes: Optional[str] = None

class PayoutOut(BaseModel):
    id: UUID
    settlement_id: UUID
    investor_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    shares_held: int
    payout_amount: Optional[float] = None
    payout_amount_inr: Optional[float] = None
    bank_ref_number: Optional[str] = None
    transfer_reference: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SettlementOut(BaseModel):
    id: UUID
    project_id: UUID
    gross_revenue: Optional[float] = None
    gross_revenue_inr: Optional[float] = None
    total_expenses: Optional[float] = None
    actual_expenses_inr: Optional[float] = None
    platform_fee: Optional[float] = None
    platform_fee_inr: Optional[float] = None
    insurance_recovered: Optional[float] = 0.0
    insurance_recovered_inr: Optional[float] = 0.0
    net_distributable: Optional[float] = None
    net_distributable_inr: Optional[float] = None
    total_investor_shares: Optional[int] = 0
    status: str
    notes: Optional[str] = None
    payouts: List[PayoutOut] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MarkTransferRequest(BaseModel):
    transfer_reference: str = Field(..., min_length=4)
