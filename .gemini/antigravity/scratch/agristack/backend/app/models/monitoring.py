import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class ActivityType(str, Enum):
    LAND_PREPARATION = "LAND_PREPARATION"
    SOWING = "SOWING"
    IRRIGATION = "IRRIGATION"
    FERTILIZER_APPLICATION = "FERTILIZER_APPLICATION"
    PEST_MANAGEMENT = "PEST_MANAGEMENT"
    INSPECTION = "INSPECTION"
    HARVEST = "HARVEST"

class FarmRecord(Base, TimestampMixin):
    __tablename__ = "farm_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    activity_type = Column(String(50), nullable=False)
    activity_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    
    # Evidence & Verification
    evidence_photo_url = Column(String(512), nullable=True)
    photo_sha256 = Column(String(64), nullable=True)
    geotag_lat = Column(Numeric(10, 7), nullable=True)
    geotag_lng = Column(Numeric(10, 7), nullable=True)
    opencv_score = Column(Numeric(5, 2), nullable=True)  # OpenCV green canopy & vegetation health score
    
    verification_status = Column(String(50), default="VERIFIED", nullable=False)  # VERIFIED, FLAGGED, PENDING

    project = relationship("Project", back_populates="farm_records")

class SensorWeatherData(Base):
    __tablename__ = "sensor_weather_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parcel_id = Column(UUID(as_uuid=True), ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    # Soil Sensors
    soil_moisture_pct = Column(Numeric(5, 2), nullable=False)
    soil_temp_c = Column(Numeric(5, 2), nullable=False)
    
    # Micro-climate
    ambient_temp_c = Column(Numeric(5, 2), nullable=False)
    humidity_pct = Column(Numeric(5, 2), nullable=False)
    rainfall_mm = Column(Numeric(6, 2), nullable=False)
    
    # Sentinel-2 Satellite Index (-1.0 to 1.0)
    ndvi_index = Column(Numeric(4, 3), nullable=False)
    source = Column(String(50), default="SIMULATED_IOT", nullable=False)

    parcel = relationship("LandParcel", back_populates="sensor_logs")
