from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class ComplianceConsentRequest(BaseModel):
    consent_type: str = Field(..., description="SEBI_CIS_SANDBOX_ACK, TERMS_OF_SERVICE, DATA_PRIVACY")
    version: str = Field(default="1.0.0")

class ComplianceConsentResponse(BaseModel):
    id: UUID
    user_id: UUID
    consent_type: str
    version: str
    ip_address: str
    agreed_at: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    actor_id: Optional[UUID] = None
    actor_role: str
    action: str
    resource_type: str
    resource_id: str
    ip_address: str
    user_agent: str
    details: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class SecurityAlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    details: Dict[str, Any]
    resolved: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
