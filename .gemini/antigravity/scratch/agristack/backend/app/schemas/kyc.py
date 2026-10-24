from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class KYCCreateRequest(BaseModel):
    # Aadhaar is received raw for validation and hashing, never stored raw in DB
    aadhaar_number: str = Field(..., min_length=12, max_length=12, description="12 digit Aadhaar number")
    pan_number: Optional[str] = Field(None, min_length=10, max_length=10)
    satbara_document_url: Optional[str] = None
    survey_number_claimed: Optional[str] = None

class KYCResponse(BaseModel):
    id: UUID
    user_id: UUID
    aadhaar_last4: str
    pan_masked: Optional[str] = None
    digilocker_uri: Optional[str] = None
    satbara_document_url: Optional[str] = None
    survey_number_claimed: Optional[str] = None
    verification_status: str
    rejection_reason: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class KYCApprovalRequest(BaseModel):
    decision: str = Field(..., description="VERIFIED or REJECTED")
    rejection_reason: Optional[str] = None
