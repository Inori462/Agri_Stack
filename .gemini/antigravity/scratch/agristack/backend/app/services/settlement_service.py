"""
Settlement service — pro-rata profit distribution to shareholders.

Formula:
  Net Distributable = Gross Revenue - Expenses - Platform Fee (5%) + Insurance Recovered
  Per-investor-share payout = Net Distributable × investor_pool_fraction / total_investor_shares

Creates Settlement + InvestorPayout records, appends SETTLEMENT_DISTRIBUTION to the ledger,
and advances the project to SETTLED state.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.core.state_machine import StateMachine
from app.models.ledger import OwnershipLedger
from app.models.escrow import Investment
from app.models.settlement import Settlement, InvestorPayout
from app.models.project import Project
from app.models.share import ShareHolding
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.ledger_service import LedgerService

logger = logging.getLogger(__name__)

PLATFORM_FEE_PCT = Decimal("0.05")  # 5 %


class SettlementService:
    @staticmethod
    def initiate_settlement(
        db: Session,
        admin: User,
        project_id: UUID,
        gross_revenue: float,
        total_expenses: float,
        insurance_recovered: float = 0.0,
        notes: Optional[str] = None,
    ) -> Settlement:
        """
        Admin calls this after harvest + verified sale to distribute returns.
        Steps:
          1. Validate project is in HARVESTED or SOLD state.
          2. Compute net distributable amount.
          3. Distribute pro-rata to investor shareholders.
          4. Create InvestorPayout rows.
          5. Append SETTLEMENT_DISTRIBUTION ledger entry.
          6. Transition project → SETTLED.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundError("Project not found")
        if project.status not in ("HARVESTED", "SOLD"):
            raise ValidationError(
                f"Settlement can only be initiated for HARVESTED/SOLD projects "
                f"(current: {project.status})"
            )

        # --- Financials ---
        gross = Decimal(str(gross_revenue))
        expenses = Decimal(str(total_expenses))
        insurance = Decimal(str(insurance_recovered))
        platform_fee = gross * PLATFORM_FEE_PCT
        net_distributable = gross - expenses - platform_fee + insurance

        logger.info(
            "Settlement calc — gross: %s  expenses: %s  fee: %s  insurance: %s  net: %s",
            gross, expenses, platform_fee, insurance, net_distributable,
        )

        # --- Investor pool fraction ---
        # Farmer equity % is stored on the project; investor pool = 1 - farmer_equity_percent
        farmer_equity_val = getattr(project, "farmer_equity_percent", getattr(project, "farmer_equity_pct", 30.0))
        farmer_equity_pct = Decimal(str(farmer_equity_val)) / Decimal("100")
        investor_pool_fraction = Decimal("1") - farmer_equity_pct

        # --- Shareholder lookup ---
        investor_holdings: List[ShareHolding] = (
            db.query(ShareHolding)
            .filter(
                ShareHolding.project_id == project_id,
                ShareHolding.holding_type.in_(["INVESTOR_PURCHASE", "INVESTOR"]),
            )
            .all()
        )
        total_investor_shares = sum(getattr(h, "share_count", getattr(h, "shares_held", 0)) for h in investor_holdings)

        # --- Create Settlement record ---
        settlement = Settlement(
            project_id=project_id,
            gross_revenue=float(gross),
            total_expenses=float(expenses),
            platform_fee=float(platform_fee),
            insurance_recovered=float(insurance),
            net_distributable=float(net_distributable),
            total_investor_shares=total_investor_shares,
            status="PROCESSING",
            initiated_by=admin.id,
            notes=notes,
        )
        db.add(settlement)
        db.flush()  # get settlement.id

        # --- Per-shareholder payouts ---
        payouts: List[InvestorPayout] = []
        if total_investor_shares > 0 and net_distributable > 0:
            per_share_amount = (
                net_distributable * investor_pool_fraction / Decimal(str(total_investor_shares))
            )
            for holding in investor_holdings:
                shares = getattr(holding, "share_count", getattr(holding, "shares_held", 0))
                payout_amount = per_share_amount * Decimal(str(shares))
                holder_id = getattr(holding, "user_id", getattr(holding, "holder_id", None))
                payout = InvestorPayout(
                    settlement_id=settlement.id,
                    project_id=project_id,
                    investor_id=holder_id,
                    user_id=holder_id,
                    shares_held=shares,
                    payout_amount=float(payout_amount),
                    status="PENDING",
                )
                db.add(payout)
                payouts.append(payout)

        settlement.status = "COMPLETED"
        settlement.completed_at = datetime.now(timezone.utc)
        db.flush()

        # --- Ledger entry ---
        LedgerService.append_entry(
            db=db,
            project_id=project_id,
            entry_type="SETTLEMENT_DISTRIBUTION",
            actor_id=admin.id,
            num_shares=total_investor_shares,
            price_per_share=float(
                net_distributable * investor_pool_fraction / Decimal(str(max(total_investor_shares, 1)))
            ),
            metadata={
                "settlement_id": str(settlement.id),
                "net_distributable": float(net_distributable),
                "platform_fee": float(platform_fee),
                "payout_count": len(payouts),
            },
        )

        # --- State transition → SETTLED ---
        StateMachine.transition(
            db=db,
            project=project,
            new_status="SETTLED",
            actor_id=admin.id,
            notes=f"Settlement {settlement.id} completed",
        )

        db.commit()
        db.refresh(settlement)

        AuditService.log_action(
            db=db,
            actor_id=admin.id,
            action="SETTLEMENT_INITIATED",
            resource_type="settlement",
            resource_id=str(settlement.id),
            details={
                "project_id": str(project_id),
                "net_distributable": float(net_distributable),
                "payout_count": len(payouts),
            },
        )
        return settlement

    @staticmethod
    def get_settlement(db: Session, project_id: UUID) -> Optional[Settlement]:
        return (
            db.query(Settlement)
            .filter(Settlement.project_id == project_id)
            .order_by(Settlement.created_at.desc())
            .first()
        )

    @staticmethod
    def get_payouts_for_investor(db: Session, investor_id: UUID) -> List[InvestorPayout]:
        return (
            db.query(InvestorPayout)
            .filter((InvestorPayout.investor_id == investor_id) | (InvestorPayout.user_id == investor_id))
            .order_by(InvestorPayout.created_at.desc())
            .all()
        )

    @staticmethod
    def mark_payout_transferred(
        db: Session,
        payout_id: UUID,
        admin: User,
        transfer_reference: str,
    ) -> InvestorPayout:
        payout = db.query(InvestorPayout).filter(InvestorPayout.id == payout_id).first()
        if not payout:
            raise NotFoundError("Payout record not found")
        payout.status = "TRANSFERRED"
        payout.transfer_reference = transfer_reference
        payout.transferred_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(payout)
        AuditService.log_action(
            db=db,
            actor_id=admin.id,
            action="PAYOUT_TRANSFERRED",
            resource_type="investor_payout",
            resource_id=str(payout.id),
            details={"reference": transfer_reference},
        )
        return payout
