import uuid
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Farm(Base, TimestampMixin):
    __tablename__ = "farms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    farm_name = Column(String(150), nullable=False)
    
    state = Column(String(100), default="Maharashtra", nullable=False)
    district = Column(String(100), nullable=False)
    taluka = Column(String(100), nullable=False)
    village = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    total_area_acres = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    farmer = relationship("User", back_populates="farms")
    parcels = relationship("LandParcel", back_populates="farm", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="farm")

class LandParcel(Base, TimestampMixin):
    __tablename__ = "land_parcels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    
    # Land Registry linkage
    survey_number = Column(String(100), nullable=False, index=True)
    sub_division_no = Column(String(50), nullable=True)
    area_acres = Column(Numeric(10, 2), nullable=False)
    
    # Geolocation & Boundary mapping (Leaflet GeoJSON polygon)
    center_latitude = Column(Numeric(10, 7), nullable=False)
    center_longitude = Column(Numeric(10, 7), nullable=False)
    boundary_geojson = Column(JSON, nullable=False)
    
    # Soil & Agronomy
    soil_type = Column(String(100), nullable=False)  # Black Cotton, Loamy, Red, Alluvial
    irrigation_source = Column(String(100), nullable=False)  # Drip, Canal, Borewell, Rainfed
    
    # Verification & Fraud checks
    is_verified = Column(Boolean, default=False, nullable=False)
    duplicate_flag = Column(Boolean, default=False, nullable=False)
    satbara_match_status = Column(String(50), default="PENDING", nullable=False)

    farm = relationship("Farm", back_populates="parcels")
    projects = relationship("Project", back_populates="parcel")
    sensor_logs = relationship("SensorWeatherData", back_populates="parcel")
