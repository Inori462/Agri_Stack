"""
Marketplace service — B2B produce listings, sale submission, APMC anomaly detection,
buyer OTP verification, and sale record finalization.
"""
from __future__ import annotations

import hashlib
import logging
import random
import string
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.marketplace import MarketplaceListing, SaleRecord
from app.models.project import Project
from app.models.user import User
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

# Maximum allowed deviation from APMC reference price before flagging
APMC_ANOMALY_THRESHOLD = 0.25  # 25 %


def _generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


class MarketplaceService:
    # -----------------------------------------------------------------------
    # Listings
    # -----------------------------------------------------------------------

    @staticmethod
    def create_listing(
        db: Session,
        farmer: User,
        project_id: UUID,
        crop_name: str,
        quantity_kg: float,
        asking_price_per_kg: float,
        description: Optional[str] = None,
    ) -> MarketplaceListing:
        """
        Farmer creates a produce listing for a project that is IN_PROGRESS or HARVESTED.
        Only the project owner may create listings.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundError("Project not found")
        if project.farmer_id != farmer.id:
            raise ForbiddenError("Only the project owner can create marketplace listings")
        if project.status not in ("IN_PROGRESS", "HARVESTED", "SOLD"):
            raise ValidationError(
                f"Listings can only be created for IN_PROGRESS/HARVESTED projects "
                f"(current: {project.status})"
            )

        listing = MarketplaceListing(
            project_id=project_id,
            farmer_id=farmer.id,
            crop_name=crop_name,
            quantity_kg=quantity_kg,
            asking_price_per_kg=asking_price_per_kg,
            description=description,
            status="ACTIVE",
        )
        db.add(listing)
        db.commit()
        db.refresh(listing)

        AuditService.log_action(
            db=db,
            actor_id=farmer.id,
            action="MARKETPLACE_LISTING_CREATED",
            resource_type="marketplace_listing",
            resource_id=str(listing.id),
            details={"crop": crop_name, "qty_kg": quantity_kg, "price": asking_price_per_kg},
        )
        return listing

    @staticmethod
    def list_active_listings(
        db: Session,
        crop_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[MarketplaceListing]:
        q = db.query(MarketplaceListing).filter(MarketplaceListing.status == "ACTIVE")
        if crop_name:
            q = q.filter(MarketplaceListing.crop_name.ilike(f"%{crop_name}%"))
        return q.offset((page - 1) * page_size).limit(page_size).all()

    @staticmethod
    def deactivate_listing(
        db: Session,
        listing_id: UUID,
        requester: User,
    ) -> MarketplaceListing:
        listing = db.query(MarketplaceListing).filter(MarketplaceListing.id == listing_id).first()
        if not listing:
            raise NotFoundError("Listing not found")
        if listing.farmer_id != requester.id and requester.primary_role not in ("ADMIN",):
            raise ForbiddenError("Not authorised to deactivate this listing")
        listing.status = "INACTIVE"
        db.commit()
        db.refresh(listing)
        return listing

    # -----------------------------------------------------------------------
    # Sale submission
    # -----------------------------------------------------------------------

    @staticmethod
    def submit_sale(
        db: Session,
        farmer: User,
        listing_id: UUID,
        buyer_name: str,
        buyer_contact: str,
        quantity_kg: float,
        sale_price_per_kg: float,
        apmc_reference_price: Optional[float],
        invoice_url: Optional[str] = None,
    ) -> SaleRecord:
        """
        Farmer submits a sale against a marketplace listing.
        APMC anomaly check: if sale price deviates >25% from APMC reference price,
        the record is flagged for admin review.
        Sends OTP to buyer for confirmation.
        """
        listing = db.query(MarketplaceListing).filter(MarketplaceListing.id == listing_id).first()
        if not listing:
            raise NotFoundError("Listing not found")
        if listing.farmer_id != farmer.id:
            raise ForbiddenError("Only listing owner can submit a sale")
        if listing.status != "ACTIVE":
            raise ValidationError("Listing is not active")

        # APMC anomaly detection
        is_flagged = False
        flag_reason = None
        if apmc_reference_price and apmc_reference_price > 0:
            deviation = abs(sale_price_per_kg - apmc_reference_price) / apmc_reference_price
            if deviation > APMC_ANOMALY_THRESHOLD:
                is_flagged = True
                flag_reason = (
                    f"Sale price {sale_price_per_kg} deviates {deviation*100:.1f}% "
                    f"from APMC reference {apmc_reference_price} (threshold 25%)"
                )
                logger.warning("APMC anomaly: %s", flag_reason)

        total_amount = Decimal(str(quantity_kg)) * Decimal(str(sale_price_per_kg))
        otp = _generate_otp()
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()

        sale = SaleRecord(
            listing_id=listing_id,
            project_id=listing.project_id,
            farmer_id=farmer.id,
            buyer_name=buyer_name,
            buyer_contact=buyer_contact,
            quantity_kg=quantity_kg,
            sale_price_per_kg=sale_price_per_kg,
            total_amount=float(total_amount),
            apmc_reference_price=apmc_reference_price,
            invoice_url=invoice_url,
            buyer_otp_hash=otp_hash,
            buyer_otp_verified=False,
            is_flagged=is_flagged,
            flag_reason=flag_reason,
            status="PENDING_VERIFICATION",
        )
        db.add(sale)

        # If flagged, mark listing as flagged too
        if is_flagged:
            listing.status = "FLAGGED"

        db.commit()
        db.refresh(sale)

        AuditService.log_action(
            db=db,
            actor_id=farmer.id,
            action="SALE_SUBMITTED",
            resource_type="sale_record",
            resource_id=str(sale.id),
            details={
                "listing_id": str(listing_id),
                "total_amount": float(total_amount),
                "flagged": is_flagged,
                "flag_reason": flag_reason,
            },
        )

        # In production, OTP would be sent via SMS/email to buyer.
        # Return OTP in response for sandbox/testing.
        sale._sandbox_otp = otp  # transient attribute for test/sandbox use
        return sale

    @staticmethod
    def verify_buyer_otp(
        db: Session,
        sale_id: UUID,
        otp: str,
    ) -> SaleRecord:
        """Buyer confirms receipt by providing OTP — marks sale as BUYER_CONFIRMED."""
        sale = db.query(SaleRecord).filter(SaleRecord.id == sale_id).first()
        if not sale:
            raise NotFoundError("Sale record not found")
        if sale.buyer_otp_verified:
            raise ValidationError("OTP already verified for this sale")

        otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        if not hmac.compare_digest(otp_hash, sale.buyer_otp_hash):
            raise ValidationError("Invalid OTP")

        sale.buyer_otp_verified = True
        sale.status = "BUYER_CONFIRMED"
        sale.verified_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(sale)
        return sale

    @staticmethod
    def get_sales_for_project(db: Session, project_id: UUID) -> List[SaleRecord]:
        return (
            db.query(SaleRecord)
            .filter(SaleRecord.project_id == project_id)
            .order_by(SaleRecord.created_at.desc())
            .all()
        )


# Fix missing import
import hmac  # noqa: E402 — needed inside verify_buyer_otp
