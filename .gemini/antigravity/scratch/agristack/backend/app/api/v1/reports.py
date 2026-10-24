"""Financial reports — P&L, harvest, investor ROI."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.marketplace import SaleRecord
from app.models.settlement import Settlement, InvestorPayout
from app.models.share import ShareHolding

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/project/{project_id}")
def project_pnl(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    sales = db.query(SaleRecord).filter(SaleRecord.project_id == project_id).all()
    settlement = db.query(Settlement).filter(Settlement.project_id == project_id).first()
    holdings = db.query(ShareHolding).filter(ShareHolding.project_id == project_id).all()
    payouts = db.query(InvestorPayout).filter(InvestorPayout.project_id == project_id).all()

    gross_sales = sum(float(s.total_amount or s.gross_revenue_inr or 0) for s in sales)
    return {
        "project_id": str(project.id),
        "title": project.title,
        "crop_name": project.crop_name,
        "status": project.status,
        "expected_revenue_inr": float(project.expected_revenue_inr),
        "gross_sales_inr": gross_sales,
        "platform_fee_inr": float(settlement.platform_fee or 0) if settlement else None,
        "net_distributable_inr": float(settlement.net_distributable or 0) if settlement else None,
        "cap_table": [
            {
                "user_id": str(h.user_id),
                "share_count": h.share_count,
                "share_percentage": float(h.share_percentage),
                "holding_type": h.holding_type,
            }
            for h in holdings
        ],
        "payouts": [
            {
                "investor_id": str(p.investor_id or p.user_id),
                "shares_held": p.shares_held,
                "payout_amount": float(p.payout_amount or 0),
                "status": p.status,
            }
            for p in payouts
        ],
        "disclaimer": "Pilot P&L. Not a SEBI-registered CIS statement.",
    }
