"""Admin operations console — KYC, anomalies, settlements, disputes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.models.kyc import KYCRecord, KYCStatus
from app.models.marketplace import SaleRecord
from app.models.dispute import CropFailureClaim, DisputeRecord
from app.models.project import Project
from app.models.settlement import Settlement

router = APIRouter(prefix="/admin", tags=["Admin Panel"])


@router.get("/overview")
def admin_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ADMIN"])),
):
    pending_kyc = db.query(KYCRecord).filter(
        KYCRecord.verification_status.in_([KYCStatus.SUBMITTED.value, KYCStatus.MANUAL_REVIEW.value])
    ).count()
    flagged_sales = db.query(SaleRecord).filter(SaleRecord.is_flagged.is_(True)).count()
    pending_claims = db.query(CropFailureClaim).filter(CropFailureClaim.status == "PENDING").count()
    open_disputes = db.query(DisputeRecord).filter(DisputeRecord.status.in_(("OPEN", "UNDER_REVIEW"))).count()
    flagged_projects = db.query(Project).filter(Project.status == "FLAGGED").count()
    settlements = db.query(Settlement).count()
    return {
        "pending_kyc": pending_kyc,
        "flagged_sales": flagged_sales,
        "pending_claims": pending_claims,
        "open_disputes": open_disputes,
        "flagged_projects": flagged_projects,
        "settlements": settlements,
        "operator": current_user.full_name,
    }
