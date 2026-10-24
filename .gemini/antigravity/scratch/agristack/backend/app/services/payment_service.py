import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.payment import PaymentTransaction, PaymentStatus
from ..models.project import Project, ProjectStatus
from ..models.share import ShareHolding, HoldingType
from ..models.escrow import Investment, EscrowStatus
from ..models.ledger import LedgerTransactionType
from ..models.user import User
from ..core.exceptions import EntityNotFoundError, AppException, PaymentVerificationError, PermissionDeniedError
from ..adapters.razorpay_adapter import RazorpayAdapter
from ..services.ledger_service import LedgerService
from ..services.audit_service import AuditService

class PaymentService:
    """Service handling Razorpay payments, idempotency, escrow holdings, and digital share acquisitions."""

    @staticmethod
    def create_investment_order(
        db: Session,
        project_id: uuid.UUID,
        user: Optional[User] = None,
        investor: Optional[User] = None,
        shares_count: Optional[int] = None,
        num_shares: Optional[int] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates a Razorpay checkout order for purchasing digital farm enterprise shares."""
        user = user or investor
        shares_count = shares_count if shares_count is not None else num_shares
        if user is None:
            raise AppException("User/investor is required")
        if shares_count is None or shares_count <= 0:
            raise AppException("Valid shares_count or num_shares is required")
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise EntityNotFoundError("Project not found")

        if project.status not in [ProjectStatus.OPEN_FOR_FUNDING.value, ProjectStatus.VERIFIED.value]:
            raise AppException(f"Project is not open for funding (current state: {project.status})")

        # Check share availability
        investor_pool_shares = int(round(project.total_shares * (float(project.investor_pool_percent) / 100.0)))
        available_shares = investor_pool_shares - project.funded_shares
        if shares_count > available_shares:
            raise AppException(f"Requested {shares_count} shares, but only {available_shares} shares remain available")

        total_amount_inr = round(shares_count * float(project.share_price_inr), 2)
        idemp_key = idempotency_key or f"idemp_{uuid.uuid4().hex}"

        # Check existing transaction by idempotency key
        existing_tx = db.query(PaymentTransaction).filter(PaymentTransaction.idempotency_key == idemp_key).first()
        if existing_tx:
            return {
                "order_id": str(existing_tx.id),
                "razorpay_order_id": existing_tx.razorpay_order_id,
                "amount_inr": float(existing_tx.amount_inr),
                "currency": existing_tx.currency,
                "key_id": RazorpayAdapter.create_order(total_amount_inr)["key_id"],
                "project_id": project.id,
                "shares_count": shares_count
            }

        rzp_order = RazorpayAdapter.create_order(
            amount_inr=total_amount_inr,
            notes={"project_id": str(project.id), "user_id": str(user.id), "shares": shares_count}
        )

        payment_tx = PaymentTransaction(
            user_id=user.id,
            project_id=project.id,
            razorpay_order_id=rzp_order["id"],
            idempotency_key=idemp_key,
            amount_inr=total_amount_inr,
            currency="INR",
            status=PaymentStatus.INITIATED.value,
            gateway_payload=rzp_order
        )
        db.add(payment_tx)
        db.commit()
        db.refresh(payment_tx)

        return {
            "order_id": str(payment_tx.id),
            "razorpay_order_id": payment_tx.razorpay_order_id,
            "amount_inr": total_amount_inr,
            "currency": "INR",
            "key_id": rzp_order["key_id"],
            "project_id": project.id,
            "shares_count": shares_count
        }

    @staticmethod
    def verify_and_capture_investment(
        db: Session,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
        user: Optional[User] = None,
        investor: Optional[User] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validates payment signature, captures escrow funds, allocates digital shares,
        and records the transaction in the tamper-evident cryptographic ownership ledger.
        """
        user = user or investor
        if user is None:
            raise AppException("User/investor is required")
        tx = db.query(PaymentTransaction).filter(PaymentTransaction.razorpay_order_id == razorpay_order_id).first()
        if not tx:
            raise EntityNotFoundError("Payment transaction not found")

        # Idempotency safety: if already captured, return success immediately
        if tx.status == PaymentStatus.CAPTURED.value:
            return {
                "success": True,
                "message": "Payment already verified and processed",
                "payment_id": tx.razorpay_payment_id,
                "status": tx.status
            }

        # Verify signature
        is_signature_valid = RazorpayAdapter.verify_payment_signature(
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature
        )
        if not is_signature_valid:
            tx.status = PaymentStatus.FAILED.value
            db.commit()
            raise PaymentVerificationError("Invalid payment signature")

        # Mark captured
        tx.status = PaymentStatus.CAPTURED.value
        tx.razorpay_payment_id = razorpay_payment_id
        tx.razorpay_signature = razorpay_signature
        tx.webhook_verified = True

        project = db.query(Project).filter(Project.id == tx.project_id).first()
        shares_to_allocate = int(round(float(tx.amount_inr) / float(project.share_price_inr)))

        # 1. Record Investment Contract with Escrow Holding
        investment = Investment(
            investor_id=user.id,
            project_id=project.id,
            share_count=shares_to_allocate,
            total_amount_inr=tx.amount_inr,
            agreement_signed=True,
            agreement_pdf_url=f"https://s3.amazonaws.com/agristack/agreements/agmt_{project.id}_{user.id}.pdf",
            payment_transaction_id=tx.id,
            escrow_status="HELD_IN_ESCROW"
        )
        db.add(investment)

        # 2. Allocate Digital Shares to Investor
        holding = (
            db.query(ShareHolding)
            .filter(ShareHolding.user_id == user.id, ShareHolding.project_id == project.id)
            .first()
        )
        share_pct = round((shares_to_allocate / project.total_shares) * 100.0, 2)
        if not holding:
            holding = ShareHolding(
                user_id=user.id,
                project_id=project.id,
                share_count=shares_to_allocate,
                share_percentage=share_pct,
                total_invested_amount_inr=tx.amount_inr,
                holding_type=HoldingType.INVESTOR_PURCHASE.value
            )
            db.add(holding)
        else:
            holding.share_count += shares_to_allocate
            holding.share_percentage += share_pct
            holding.total_invested_amount_inr += tx.amount_inr

        # 3. Update project funded count
        project.funded_shares += shares_to_allocate
        investor_target_pool = int(round(project.total_shares * (float(project.investor_pool_percent) / 100.0)))

        # If 100% of public shares funded, advance state to FUNDED!
        if project.funded_shares >= investor_target_pool:
            project.status = ProjectStatus.FUNDED.value

        db.commit()

        # 4. Cryptographic Ownership Ledger Entry
        ledger_entry = LedgerService.append_entry(
            db=db,
            project_id=project.id,
            transaction_type=LedgerTransactionType.SHARE_PURCHASE.value,
            to_user_id=user.id,
            shares_count=shares_to_allocate,
            price_per_share=float(project.share_price_inr),
            total_amount=float(tx.amount_inr),
            from_user_id=project.farmer_id
        )

        AuditService.log_action(
            db=db,
            action="SHARE_INVESTMENT_CAPTURED",
            resource_type="INVESTMENT",
            resource_id=str(investment.id),
            actor_role=user.primary_role,
            actor_id=user.id,
            details={
                "project_id": str(project.id),
                "shares_purchased": shares_to_allocate,
                "amount_inr": float(tx.amount_inr),
                "ledger_entry_hash": ledger_entry.entry_hash
            }
        )

        return {
            "success": True,
            "message": "Investment processed and digital shares allocated",
            "investment_id": str(investment.id),
            "project_id": str(project.id),
            "shares_purchased": shares_to_allocate,
            "project_status": project.status,
            "ledger_entry_hash": ledger_entry.entry_hash
        }
