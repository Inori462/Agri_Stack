from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class ShareHoldingResponse(BaseModel):
    id: UUID
    user_id: UUID
    project_id: UUID
    share_count: int
    share_percentage: float
    total_invested_amount_inr: float
    holding_type: str
    is_locked: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SharePurchaseRequest(BaseModel):
    project_id: UUID
    shares_count: int = Field(..., gt=0, le=50, description="Number of digital shares to acquire")
    agreement_accepted: bool = Field(..., description="Must accept fractional pilot agreement terms")

class LedgerEntryResponse(BaseModel):
    sequence_id: int
    entry_id: UUID
    project_id: UUID
    prev_hash: str
    entry_hash: str
    transaction_type: str
    from_user_id: Optional[UUID] = None
    to_user_id: UUID
    shares_count: int
    price_per_share_inr: float
    total_amount_inr: float
    timestamp: datetime
    signature: str

    class Config:
        from_attributes = True

class LedgerIntegrityResponse(BaseModel):
    project_id: UUID
    is_valid: bool
    entries_audited: int
    error_count: int
    errors: List[str]
    audit_timestamp: datetime
