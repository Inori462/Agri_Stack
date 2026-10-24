from typing import List, Optional
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class ClaimCreate(BaseModel):
    project_id: UUID
    incident_type: str = Field(..., description="UNSEASONAL_RAINFALL, DROUGHT, HAILSTORM, PEST_ATTACK")
    incident_date: Optional[date] = None
    estimated_damage_pct: float = Field(..., ge=1.0, le=100.0)
    insurance_policy_no: Optional[str] = None
    evidence_photos: List[str] = Field(default=[], description="List of S3 photo links")

class ClaimResponse(BaseModel):
    id: UUID
    project_id: UUID
    farmer_id: UUID
    incident_type: Optional[str] = None
    failure_reason: Optional[str] = None
    incident_date: Optional[date] = None
    estimated_damage_pct: Optional[float] = None
    affected_area_pct: Optional[float] = None
    insurance_policy_no: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    evidence_photos: Optional[List[str]] = []
    evidence_urls: Optional[List[str]] = []
    admin_status: Optional[str] = None
    status: Optional[str] = None
    approved_insurance_amount_inr: Optional[float] = 0.0
    insurance_approved_amount: Optional[float] = 0.0
    refund_pool_amount_inr: Optional[float] = 0.0
    resolution_notes: Optional[str] = None
    admin_notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Phase 5 Disputes Router Schemas
class CropFailureClaimRequest(BaseModel):
    project_id: UUID
    failure_reason: str = Field(..., min_length=3)
    affected_area_pct: float = Field(..., ge=0.1, le=100.0)
    evidence_urls: Optional[List[str]] = []
    insurance_policy_number: Optional[str] = None

class CropFailureClaimOut(BaseModel):
    id: UUID
    project_id: UUID
    farmer_id: UUID
    failure_reason: Optional[str] = None
    incident_type: Optional[str] = None
    affected_area_pct: Optional[float] = None
    estimated_damage_pct: Optional[float] = None
    insurance_policy_number: Optional[str] = None
    insurance_policy_no: Optional[str] = None
    evidence_urls: Optional[List[str]] = []
    evidence_photos: Optional[List[str]] = []
    status: str
    insurance_approved_amount: Optional[float] = 0.0
    approved_insurance_amount_inr: Optional[float] = 0.0
    admin_notes: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReviewClaimRequest(BaseModel):
    decision: str = Field(..., description="APPROVED or REJECTED")
    insurance_approved_amount: Optional[float] = 0.0
    admin_notes: Optional[str] = None

class DisputeRequest(BaseModel):
    project_id: UUID
    dispute_type: str = Field(..., min_length=3)
    description: str = Field(..., min_length=5)
    evidence_urls: Optional[List[str]] = []

class DisputeOut(BaseModel):
    id: UUID
    project_id: UUID
    raised_by: Optional[UUID] = None
    raised_by_user_id: Optional[UUID] = None
    dispute_type: Optional[str] = None
    dispute_category: Optional[str] = None
    description: Optional[str] = None
    claim_details: Optional[str] = None
    status: str
    resolution: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ResolveDisputeRequest(BaseModel):
    resolution: str = Field(..., min_length=3)
    resolution_notes: Optional[str] = None
