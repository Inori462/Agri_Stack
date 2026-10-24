"""
Marketplace router — produce listings and sale management.
"""
from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.user import User
from app.schemas.marketplace import (
    CreateListingRequest,
    ListingOut,
    SubmitSaleRequest,
    SaleRecordOut,
    VerifyOTPRequest,
)
from app.services.marketplace_service import MarketplaceService

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.post(
    "/listings",
    response_model=ListingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create produce listing",
)
def create_listing(
    body: CreateListingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["FARMER", "ADMIN"])),
):
    return MarketplaceService.create_listing(
        db=db,
        farmer=current_user,
        project_id=body.project_id,
        crop_name=body.crop_name,
        quantity_kg=body.quantity_kg,
        asking_price_per_kg=body.asking_price_per_kg,
        description=body.description,
    )


@router.get(
    "/listings",
    response_model=List[ListingOut],
    summary="Browse active produce listings",
)
def list_listings(
    crop_name: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MarketplaceService.list_active_listings(
        db=db, crop_name=crop_name, page=page, page_size=page_size
    )


@router.delete(
    "/listings/{listing_id}",
    response_model=ListingOut,
    summary="Deactivate a listing",
)
def deactivate_listing(
    listing_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["FARMER", "ADMIN"])),
):
    return MarketplaceService.deactivate_listing(db=db, listing_id=listing_id, requester=current_user)


@router.post(
    "/sales",
    response_model=SaleRecordOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a produce sale (triggers buyer OTP)",
)
def submit_sale(
    body: SubmitSaleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["FARMER", "ADMIN"])),
):
    return MarketplaceService.submit_sale(
        db=db,
        farmer=current_user,
        listing_id=body.listing_id,
        buyer_name=body.buyer_name,
        buyer_contact=body.buyer_contact,
        quantity_kg=body.quantity_kg,
        sale_price_per_kg=body.sale_price_per_kg,
        apmc_reference_price=body.apmc_reference_price,
        invoice_url=body.invoice_url,
    )


@router.post(
    "/sales/{sale_id}/verify-otp",
    response_model=SaleRecordOut,
    summary="Buyer confirms sale via OTP",
)
def verify_sale_otp(
    sale_id: UUID,
    body: VerifyOTPRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MarketplaceService.verify_buyer_otp(db=db, sale_id=sale_id, otp=body.otp)


@router.get(
    "/sales/project/{project_id}",
    response_model=List[SaleRecordOut],
    summary="Get all sale records for a project",
)
def project_sales(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MarketplaceService.get_sales_for_project(db=db, project_id=project_id)
