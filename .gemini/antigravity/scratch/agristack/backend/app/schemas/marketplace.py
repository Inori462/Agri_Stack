from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class MarketplaceListingCreate(BaseModel):
    project_id: UUID
    crop_name: str
    grade: str = "Grade A"
    quantity_kg: float = Field(..., gt=0)
    price_per_kg_inr: float = Field(..., gt=0)
    min_order_kg: float = Field(default=50.0, gt=0)

class MarketplaceListingResponse(BaseModel):
    id: UUID
    project_id: UUID
    crop_name: str
    grade: Optional[str] = "Grade A"
    quantity_kg: float
    price_per_kg_inr: Optional[float] = None
    asking_price_per_kg: Optional[float] = None
    min_order_kg: Optional[float] = 50.0
    status: str
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SaleRecordCreate(BaseModel):
    project_id: UUID
    listing_id: Optional[UUID] = None
    buyer_name: str = Field(..., min_length=2)
    buyer_contact: str
    quantity_sold_kg: float = Field(..., gt=0)
    price_per_kg_inr: float = Field(..., gt=0)
    invoice_url: Optional[str] = Field(None, description="Uploaded invoice URL")
    buyer_otp: Optional[str] = None

class SaleRecordResponse(BaseModel):
    id: UUID
    project_id: UUID
    listing_id: Optional[UUID] = None
    buyer_name: str
    buyer_contact: str
    quantity_sold_kg: Optional[float] = None
    quantity_kg: Optional[float] = None
    price_per_kg_inr: Optional[float] = None
    sale_price_per_kg: Optional[float] = None
    gross_revenue_inr: Optional[float] = None
    total_amount: Optional[float] = None
    buyer_otp_verified: bool
    apmc_modal_price: Optional[float] = None
    apmc_reference_price: Optional[float] = None
    price_anomaly_flag: Optional[bool] = False
    is_flagged: Optional[bool] = False
    flag_reason: Optional[str] = None
    invoice_url: Optional[str] = None
    status: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Phase 5 Marketplace Router Schemas
class CreateListingRequest(BaseModel):
    project_id: UUID
    crop_name: str
    quantity_kg: float = Field(..., gt=0)
    asking_price_per_kg: float = Field(..., gt=0)
    description: Optional[str] = None

class ListingOut(BaseModel):
    id: UUID
    project_id: UUID
    farmer_id: Optional[UUID] = None
    crop_name: str
    quantity_kg: float
    asking_price_per_kg: Optional[float] = None
    price_per_kg_inr: Optional[float] = None
    description: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SubmitSaleRequest(BaseModel):
    listing_id: UUID
    buyer_name: str = Field(..., min_length=2)
    buyer_contact: str = Field(..., min_length=6)
    quantity_kg: float = Field(..., gt=0)
    sale_price_per_kg: float = Field(..., gt=0)
    apmc_reference_price: Optional[float] = None
    invoice_url: Optional[str] = None

class SaleRecordOut(BaseModel):
    id: UUID
    listing_id: Optional[UUID] = None
    project_id: UUID
    farmer_id: Optional[UUID] = None
    buyer_name: str
    buyer_contact: str
    quantity_kg: Optional[float] = None
    quantity_sold_kg: Optional[float] = None
    sale_price_per_kg: Optional[float] = None
    price_per_kg_inr: Optional[float] = None
    total_amount: Optional[float] = None
    gross_revenue_inr: Optional[float] = None
    apmc_reference_price: Optional[float] = None
    buyer_otp_verified: bool = False
    is_flagged: bool = False
    flag_reason: Optional[str] = None
    status: str
    invoice_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VerifyOTPRequest(BaseModel):
    otp: str = Field(..., min_length=4, max_length=10)
