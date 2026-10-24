from typing import Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class PaymentOrderCreate(BaseModel):
    project_id: UUID
    shares_count: int = Field(..., gt=0)

class PaymentOrderResponse(BaseModel):
    order_id: str
    razorpay_order_id: str
    amount_inr: float
    currency: str = "INR"
    key_id: str
    project_id: UUID
    shares_count: int

    model_config = ConfigDict(from_attributes=True)

class PaymentVerificationRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    idempotency_key: Optional[str] = None

class PaymentTransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    project_id: Optional[UUID] = None
    razorpay_order_id: str
    razorpay_payment_id: Optional[str] = None
    amount_inr: float
    currency: str
    status: str
    webhook_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Phase 5 REST Schemas
class CreateOrderRequest(BaseModel):
    project_id: UUID
    num_shares: int = Field(..., gt=0)

    @property
    def shares_count(self) -> int:
        return self.num_shares

class CreateOrderResponse(BaseModel):
    order_id: str
    razorpay_order_id: str
    amount_inr: float
    currency: str = "INR"
    key_id: str
    project_id: UUID
    shares_count: Optional[int] = None
    num_shares: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    idempotency_key: Optional[str] = None

class VerifyPaymentResponse(BaseModel):
    success: bool
    message: str
    payment_id: Optional[str] = None
    investment_id: Optional[str] = None
    project_id: Optional[str] = None
    shares_purchased: Optional[int] = None
    project_status: Optional[str] = None
    ledger_entry_hash: Optional[str] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class InvestmentOut(BaseModel):
    id: UUID
    investor_id: UUID
    project_id: UUID
    share_count: int
    total_amount_inr: float
    agreement_signed: bool
    agreement_pdf_url: Optional[str] = None
    escrow_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
