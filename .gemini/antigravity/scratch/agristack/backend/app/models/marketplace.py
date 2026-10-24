import uuid
from enum import Enum
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class ListingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    NEGOTIATING = "NEGOTIATING"
    SOLD = "SOLD"
    INACTIVE = "INACTIVE"
    FLAGGED = "FLAGGED"

class MarketplaceListing(Base, TimestampMixin):
    __tablename__ = "marketplace_listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    crop_name = Column(String(100), nullable=False)
    grade = Column(String(50), default="Grade A", nullable=False)
    quantity_kg = Column(Numeric(10, 2), nullable=False)
    price_per_kg_inr = Column(Numeric(8, 2), nullable=True)
    asking_price_per_kg = Column(Numeric(8, 2), nullable=True)
    min_order_kg = Column(Numeric(10, 2), default=50.00, nullable=False)
    description = Column(String(500), nullable=True)
    
    status = Column(String(50), default=ListingStatus.ACTIVE.value, nullable=False)

    project = relationship("Project", back_populates="marketplace_listings")
    sale_record = relationship("SaleRecord", back_populates="listing", uselist=False)

    def __init__(self, **kwargs):
        if "asking_price_per_kg" in kwargs and "price_per_kg_inr" not in kwargs:
            kwargs["price_per_kg_inr"] = kwargs["asking_price_per_kg"]
        elif "price_per_kg_inr" in kwargs and "asking_price_per_kg" not in kwargs:
            kwargs["asking_price_per_kg"] = kwargs["price_per_kg_inr"]
        super().__init__(**kwargs)

class SaleRecord(Base, TimestampMixin):
    __tablename__ = "sale_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(UUID(as_uuid=True), ForeignKey("marketplace_listings.id"), nullable=True)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    buyer_name = Column(String(150), nullable=False)
    buyer_contact = Column(String(50), nullable=False)
    quantity_sold_kg = Column(Numeric(10, 2), nullable=True)
    quantity_kg = Column(Numeric(10, 2), nullable=True)
    price_per_kg_inr = Column(Numeric(8, 2), nullable=True)
    sale_price_per_kg = Column(Numeric(8, 2), nullable=True)
    gross_revenue_inr = Column(Numeric(12, 2), nullable=True)
    total_amount = Column(Numeric(12, 2), nullable=True)
    
    # Fraud Prevention & Verification
    buyer_otp_hash = Column(String(128), nullable=True)
    buyer_otp_verified = Column(Boolean, default=False, nullable=False)
    apmc_modal_price = Column(Numeric(8, 2), nullable=True)
    apmc_reference_price = Column(Numeric(8, 2), nullable=True)
    price_anomaly_flag = Column(Boolean, default=False, nullable=False)
    is_flagged = Column(Boolean, default=False, nullable=False)
    flag_reason = Column(String(500), nullable=True)
    invoice_url = Column(String(512), nullable=True)
    status = Column(String(50), default="PENDING_VERIFICATION", nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="sale_record")
    listing = relationship("MarketplaceListing", back_populates="sale_record")

    def __init__(self, **kwargs):
        if "quantity_kg" in kwargs and "quantity_sold_kg" not in kwargs:
            kwargs["quantity_sold_kg"] = kwargs["quantity_kg"]
        elif "quantity_sold_kg" in kwargs and "quantity_kg" not in kwargs:
            kwargs["quantity_kg"] = kwargs["quantity_sold_kg"]

        if "sale_price_per_kg" in kwargs and "price_per_kg_inr" not in kwargs:
            kwargs["price_per_kg_inr"] = kwargs["sale_price_per_kg"]
        elif "price_per_kg_inr" in kwargs and "sale_price_per_kg" not in kwargs:
            kwargs["sale_price_per_kg"] = kwargs["price_per_kg_inr"]

        if "total_amount" in kwargs and "gross_revenue_inr" not in kwargs:
            kwargs["gross_revenue_inr"] = kwargs["total_amount"]
        elif "gross_revenue_inr" in kwargs and "total_amount" not in kwargs:
            kwargs["total_amount"] = kwargs["gross_revenue_inr"]

        if "is_flagged" in kwargs and "price_anomaly_flag" not in kwargs:
            kwargs["price_anomaly_flag"] = kwargs["is_flagged"]
        elif "price_anomaly_flag" in kwargs and "is_flagged" not in kwargs:
            kwargs["is_flagged"] = kwargs["price_anomaly_flag"]

        if "apmc_reference_price" in kwargs and "apmc_modal_price" not in kwargs:
            kwargs["apmc_modal_price"] = kwargs["apmc_reference_price"]
        elif "apmc_modal_price" in kwargs and "apmc_reference_price" not in kwargs:
            kwargs["apmc_reference_price"] = kwargs["apmc_modal_price"]

        super().__init__(**kwargs)
