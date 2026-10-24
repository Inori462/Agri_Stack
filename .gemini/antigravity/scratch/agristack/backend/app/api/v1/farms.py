from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.dependencies import get_current_user
from ...models.user import User, UserRole
from ...models.farm import Farm, LandParcel
from ...schemas.farm import FarmCreate, FarmResponse, LandParcelCreate, LandParcelResponse
from ...services.farm_service import FarmService
from ...core.exceptions import EntityNotFoundError, PermissionDeniedError

router = APIRouter(prefix="/farms", tags=["Farms & Land Parcels"])

@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(
    req: FarmCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registers a new farm enterprise. Only registered farmers or admins can create farms."""
    if current_user.primary_role not in [UserRole.FARMER.value, UserRole.ADMIN.value]:
        raise PermissionDeniedError("Only farmers can register farms")
    return FarmService.create_farm(db=db, farmer=current_user, data=req)

@router.get("", response_model=List[FarmResponse])
def list_farms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists farms. Farmers view their own farms; Admins view all platform farms."""
    query = db.query(Farm)
    if current_user.primary_role == UserRole.FARMER.value:
        query = query.filter(Farm.farmer_id == current_user.id)
    return query.order_by(Farm.created_at.desc()).all()

@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(
    farm_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves full farm entity with associated land parcels and GeoJSON boundaries."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise EntityNotFoundError("Farm not found")
    if current_user.primary_role == UserRole.FARMER.value and farm.farmer_id != current_user.id:
        raise PermissionDeniedError("Access denied: You do not own this farm enterprise")
    return farm

@router.post("/{farm_id}/parcels", response_model=LandParcelResponse, status_code=status.HTTP_201_CREATED)
def add_parcel(
    farm_id: UUID,
    req: LandParcelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adds a land parcel with boundary polygon to a farm."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise EntityNotFoundError("Farm not found")
    if current_user.primary_role == UserRole.FARMER.value and farm.farmer_id != current_user.id:
        raise PermissionDeniedError("Access denied: You do not own this farm enterprise")
    return FarmService.add_land_parcel(db=db, farm=farm, farmer=current_user, data=req)
