from typing import Optional
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field

class FarmRecordCreate(BaseModel):
    project_id: UUID
    activity_type: str = Field(..., description="SOWING, IRRIGATION, FERTILIZER_APPLICATION, PEST_MANAGEMENT, HARVEST")
    activity_date: date
    description: str = Field(..., min_length=5)
    evidence_photo_url: Optional[str] = None
    geotag_lat: Optional[float] = None
    geotag_lng: Optional[float] = None

class FarmRecordResponse(BaseModel):
    id: UUID
    project_id: UUID
    activity_type: str
    activity_date: date
    description: str
    evidence_photo_url: Optional[str] = None
    photo_sha256: Optional[str] = None
    geotag_lat: Optional[float] = None
    geotag_lng: Optional[float] = None
    opencv_score: Optional[float] = None
    verification_status: str
    created_at: datetime

    class Config:
        from_attributes = True

class SensorDataResponse(BaseModel):
    id: UUID
    parcel_id: UUID
    recorded_at: datetime
    soil_moisture_pct: float
    soil_temp_c: float
    ambient_temp_c: float
    humidity_pct: float
    rainfall_mm: float
    ndvi_index: float
    source: str

    class Config:
        from_attributes = True
