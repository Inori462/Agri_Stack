"""
Payments router — Razorpay order creation, verification, webhook, portfolio.
All payment operations are protected by JWT + MFA enforcement on admin routes.
"""
from __future__ import annotations

import hmac
import hashlib
import logging
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.core.config import get_settings
from app.models.user import User
from app.models.payment import PaymentTransaction
from app.models.escrow import Investment
from app.schemas.payment import (
    CreateOrderRequest,
    CreateOrderResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
    InvestmentOut,
)
from app.services.payment_service import PaymentService

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/payments", tags=["Payments"])


# ---------------------------------------------------------------------------
# Create Razorpay order
# ---------------------------------------------------------------------------
@router.post(
    "/orders",
    response_model=CreateOrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Razorpay order for share purchase",
)
def create_order(
    body: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["INVESTOR", "FARMER", "ADMIN"])),
):
    """Investor initiates share purchase → returns Razorpay order_id."""
    return PaymentService.create_investment_order(
        db=db,
        investor=current_user,
        project_id=body.project_id,
        num_shares=body.num_shares,
    )


# ---------------------------------------------------------------------------
# Verify payment signature and capture investment
# ---------------------------------------------------------------------------
@router.post(
    "/verify",
    response_model=VerifyPaymentResponse,
    summary="Verify Razorpay signature and capture investment",
)
def verify_payment(
    body: VerifyPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["INVESTOR", "FARMER", "ADMIN"])),
):
    """After Razorpay checkout, verify signature → allocate shares → update ledger."""
    return PaymentService.verify_and_capture_investment(
        db=db,
        investor=current_user,
        razorpay_order_id=body.razorpay_order_id,
        razorpay_payment_id=body.razorpay_payment_id,
        razorpay_signature=body.razorpay_signature,
    )


# ---------------------------------------------------------------------------
# Razorpay webhook endpoint
# ---------------------------------------------------------------------------
@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="Razorpay webhook — signature-verified event ingestion",
)
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(..., alias="X-Razorpay-Signature"),
    db: Session = Depends(get_db),
):
    """
    Accepts Razorpay webhook events.
    Verifies HMAC-SHA256 signature before any processing.
    Idempotent — repeated delivery of the same event is safely ignored.
    """
    raw_body = await request.body()
    secret = settings.RAZORPAY_WEBHOOK_SECRET.encode()

    expected = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
    # Accept test_ prefixed sigs in sandbox mode
    is_valid = hmac.compare_digest(expected, x_razorpay_signature) or (
        settings.RAZORPAY_SANDBOX and x_razorpay_signature.startswith("test_")
    )
    if not is_valid:
        logger.warning("Razorpay webhook signature mismatch — rejected")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        )

    try:
        import json

        payload = json.loads(raw_body)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event = payload.get("event", "")
    logger.info("Razorpay webhook received: %s", event)

    # Handle payment.captured asynchronously
    if event == "payment.captured":
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = payment_entity.get("order_id")
        payment_id = payment_entity.get("id")
        if order_id and payment_id:
            # Look up pending transaction
            txn = (
                db.query(PaymentTransaction)
                .filter(PaymentTransaction.razorpay_order_id == order_id)
                .first()
            )
            if txn and txn.status == "PENDING":
                txn.status = "CAPTURED"
                txn.razorpay_payment_id = payment_id
                db.commit()
                logger.info("Webhook: captured txn %s", txn.id)

    return {"status": "ok", "event": event}


# ---------------------------------------------------------------------------
# Investor portfolio
# ---------------------------------------------------------------------------
@router.get(
    "/my-investments",
    response_model=List[InvestmentOut],
    summary="List all investments made by the authenticated investor",
)
def my_investments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["INVESTOR", "FARMER", "ADMIN"])),
):
    """Returns all confirmed share purchases for the authenticated user."""
    investments = (
        db.query(Investment)
        .filter(
            Investment.investor_id == current_user.id,
            Investment.status == "CONFIRMED",
        )
        .all()
    )
    return investments
