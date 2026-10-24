import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.farm import Farm, LandParcel
from ..models.user import User
from ..schemas.farm import FarmCreate, LandParcelCreate
from ..adapters.satbara_adapter import SatbaraAdapter
from ..core.exceptions import EntityNotFoundError, AppException
from ..services.audit_service import AuditService

class FarmService:
    """Service managing Farm enterprises, Land parcels, boundaries, and 7/12 Satbara cross-checks."""

    @staticmethod
    def create_farm(db: Session, farmer: User, data: FarmCreate) -> Farm:
        """Registers a new farm enterprise for the farmer."""
        farm = Farm(
            farmer_id=farmer.id,
            farm_name=data.farm_name,
            state=data.state,
            district=data.district,
            taluka=data.taluka,
            village=data.village,
            pincode=data.pincode,
            total_area_acres=data.total_area_acres
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)

        # If initial parcels provided in payload
        if data.parcels:
            for p_data in data.parcels:
                FarmService.add_land_parcel(db=db, farm=farm, farmer=farmer, data=p_data)

        db.refresh(farm)
        return farm

    @staticmethod
    def add_land_parcel(db: Session, farm: Farm, farmer: User, data: LandParcelCreate) -> LandParcel:
        """
        Registers a land parcel with Leaflet GeoJSON boundary polygon.
        Executes duplicate survey number detection and Satbara 7/12 registry check.
        """
        # Fraud check: Duplicate survey number within the same taluka & district
        duplicate_existing = (
            db.query(LandParcel)
            .join(Farm)
            .filter(
                LandParcel.survey_number == data.survey_number,
                Farm.district == farm.district,
                Farm.taluka == farm.taluka,
                Farm.farmer_id != farmer.id
            )
            .first()
        )

        has_duplicate_flag = bool(duplicate_existing)
        if has_duplicate_flag:
            AuditService.record_security_alert(
                db=db,
                alert_type="DUPLICATE_SURVEY_NUMBER_DETECTED",
                severity="HIGH",
                details={
                    "survey_number": data.survey_number,
                    "district": farm.district,
                    "taluka": farm.taluka,
                    "claiming_farmer_id": str(farmer.id),
                    "conflicting_farm_id": str(duplicate_existing.farm_id)
                }
            )

        # Execute automated 7/12 Satbara registry cross-check
        satbara_result = SatbaraAdapter.verify_satbara_record(
            survey_number=data.survey_number,
            sub_division=data.sub_division_no,
            district=farm.district,
            taluka=farm.taluka,
            village=farm.village,
            declared_acres=data.area_acres,
            farmer_name=farmer.full_name
        )

        parcel = LandParcel(
            farm_id=farm.id,
            survey_number=data.survey_number,
            sub_division_no=data.sub_division_no,
            area_acres=data.area_acres,
            center_latitude=data.center_latitude,
            center_longitude=data.center_longitude,
            boundary_geojson=data.boundary_geojson,
            soil_type=data.soil_type,
            irrigation_source=data.irrigation_source,
            is_verified=satbara_result["is_verified"] and not has_duplicate_flag,
            duplicate_flag=has_duplicate_flag,
            satbara_match_status=satbara_result["status"]
        )

        db.add(parcel)
        db.commit()
        db.refresh(parcel)

        AuditService.log_action(
            db=db,
            action="LAND_PARCEL_REGISTERED",
            resource_type="LAND_PARCEL",
            resource_id=str(parcel.id),
            actor_role=farmer.primary_role,
            actor_id=farmer.id,
            details={
                "survey_number": data.survey_number,
                "is_verified": parcel.is_verified,
                "duplicate_flag": has_duplicate_flag
            }
        )

        return parcel
