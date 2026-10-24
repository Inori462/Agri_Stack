from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    farm_id: UUID
    parcel_id: UUID
    title: str = Field(..., min_length=3)
    crop_name: str
    crop_variety: str
    season: str = Field(..., description="Kharif, Rabi, Zaid")
    sowing_date: date
    estimated_harvest_date: date
    
    total_valuation_inr: float = Field(..., gt=0)
    farmer_equity_percent: float = Field(default=30.00, ge=10.0, le=90.0)
    total_shares: int = Field(default=100, ge=10, le=1000)
    expected_yield_quintals: float = Field(..., gt=0)
    expected_revenue_inr: float = Field(..., gt=0)

class ProjectStateLogResponse(BaseModel):
    id: UUID
    from_state: str
    to_state: str
    actor_id: Optional[UUID] = None
    rationale: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectResponse(BaseModel):
    id: UUID
    farm_id: UUID
    parcel_id: UUID
    farmer_id: UUID
    title: str
    crop_name: str
    crop_variety: str
    season: str
    sowing_date: date
    estimated_harvest_date: date
    status: str
    total_valuation_inr: float
    farmer_equity_percent: float
    investor_pool_percent: float
    total_shares: int
    share_price_inr: float
    funded_shares: int
    expected_yield_quintals: float
    expected_revenue_inr: float
    risk_score: int
    created_at: datetime
    state_logs: List[ProjectStateLogResponse] = []

    class Config:
        from_attributes = True

class ProjectTransitionRequest(BaseModel):
    next_state: str = Field(..., description="Target state in state machine")
    rationale: Optional[str] = Field(None, description="Reason or verification remarks")
    remarks: Optional[str] = Field(None, description="Alias used by clients/tests")
    metadata: Optional[Dict[str, Any]] = None
