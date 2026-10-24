from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class LandParcelCreate(BaseModel):
    survey_number: str = Field(..., description="Survey/Gat Number from 7/12 record")
    sub_division_no: Optional[str] = None
    area_acres: float = Field(..., gt=0)
    center_latitude: float
    center_longitude: float
    boundary_geojson: Dict[str, Any] = Field(..., description="GeoJSON polygon coordinates")
    soil_type: str = Field(..., description="Black Cotton, Loamy, Red, Alluvial")
    irrigation_source: str = Field(..., description="Drip, Canal, Borewell, Rainfed")

class LandParcelResponse(BaseModel):
    id: UUID
    farm_id: UUID
    survey_number: str
    sub_division_no: Optional[str] = None
    area_acres: float
    center_latitude: float
    center_longitude: float
    boundary_geojson: Dict[str, Any]
    soil_type: str
    irrigation_source: str
    is_verified: bool
    duplicate_flag: bool
    satbara_match_status: str
    created_at: datetime

    class Config:
        from_attributes = True

class FarmCreate(BaseModel):
    farm_name: str = Field(..., min_length=2)
    state: str = "Maharashtra"
    district: str
    taluka: str
    village: str
    pincode: str
    total_area_acres: float = Field(..., gt=0)
    parcels: Optional[List[LandParcelCreate]] = None

class FarmResponse(BaseModel):
    id: UUID
    farmer_id: UUID
    farm_name: str
    state: str
    district: str
    taluka: str
    village: str
    pincode: str
    total_area_acres: float
    is_active: bool
    created_at: datetime
    parcels: List[LandParcelResponse] = []

    class Config:
        from_attributes = True
