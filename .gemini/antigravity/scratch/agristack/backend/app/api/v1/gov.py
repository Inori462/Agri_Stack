"""Government/society anonymized district heatmap and income-uplift stats."""
from __future__ import annotations

from collections import defaultdict
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_roles, get_current_user
from app.models.farm import Farm
from app.models.project import Project
from app.models.user import User
from app.models.settlement import Settlement

router = APIRouter(prefix="/gov", tags=["Government & Society Dashboard"])

DISTRICT_COORDS = {
    "Pune": {"lat": 18.52, "lng": 73.85},
    "Nashik": {"lat": 19.99, "lng": 73.78},
    "Nagpur": {"lat": 21.15, "lng": 79.09},
    "Aurangabad": {"lat": 19.88, "lng": 75.34},
    "Kolhapur": {"lat": 16.70, "lng": 74.24},
    "Satara": {"lat": 17.68, "lng": 74.00},
    "Solapur": {"lat": 17.66, "lng": 75.90},
    "Baramati": {"lat": 18.15, "lng": 74.58},
}


@router.get("/heatmap")
def district_heatmap(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["GOV_OFFICER", "ADMIN"])),
):
    """Anonymized district-level project, risk, and settlement aggregates."""
    rows: List[Project] = db.query(Project).all()
    farms = {f.id: f for f in db.query(Farm).all()}
    settlements = {s.project_id: s for s in db.query(Settlement).all()}

    buckets = defaultdict(lambda: {
        "district": "",
        "project_count": 0,
        "avg_risk": 0.0,
        "risk_sum": 0,
        "funded_inr": 0.0,
        "settled_inr": 0.0,
        "open_for_funding": 0,
        "in_progress": 0,
        "settled": 0,
    })

    for p in rows:
        farm = farms.get(p.farm_id)
        district = farm.district if farm else "Unknown"
        b = buckets[district]
        b["district"] = district
        b["project_count"] += 1
        b["risk_sum"] += int(p.risk_score or 0)
        b["funded_inr"] += float(p.share_price_inr or 0) * int(p.funded_shares or 0)
        if p.status == "OPEN_FOR_FUNDING":
            b["open_for_funding"] += 1
        if p.status == "IN_PROGRESS":
            b["in_progress"] += 1
        if p.status in ("SETTLED", "CLOSED"):
            b["settled"] += 1
        st = settlements.get(p.id)
        if st:
            b["settled_inr"] += float(st.net_distributable or st.net_distributable_inr or 0)

    points = []
    for district, b in buckets.items():
        count = max(b["project_count"], 1)
        coords = DISTRICT_COORDS.get(district, {"lat": 19.75, "lng": 75.71})
        avg_risk = round(b["risk_sum"] / count, 1)
        points.append({
            "district": district,
            "lat": coords["lat"],
            "lng": coords["lng"],
            "project_count": b["project_count"],
            "avg_risk": avg_risk,
            "risk_band": "LOW" if avg_risk < 35 else "MEDIUM" if avg_risk < 65 else "HIGH",
            "funded_inr": round(b["funded_inr"], 2),
            "settled_inr": round(b["settled_inr"], 2),
            "open_for_funding": b["open_for_funding"],
            "in_progress": b["in_progress"],
            "settled": b["settled"],
        })

    if not points:
        points = [
            {
                "district": "Pune",
                "lat": 18.52,
                "lng": 73.85,
                "project_count": 0,
                "avg_risk": 28,
                "risk_band": "LOW",
                "funded_inr": 0,
                "settled_inr": 0,
                "open_for_funding": 0,
                "in_progress": 0,
                "settled": 0,
            }
        ]

    return {
        "state": "Maharashtra",
        "anonymized": True,
        "disclaimer": "Aggregates only. No Aadhaar, land title, or investor PII is exposed.",
        "points": points,
        "viewer_role": current_user.primary_role,
    }


@router.get("/summary")
def gov_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = db.query(Project).all()
    return {
        "total_projects": len(projects),
        "open_for_funding": sum(1 for p in projects if p.status == "OPEN_FOR_FUNDING"),
        "in_progress": sum(1 for p in projects if p.status == "IN_PROGRESS"),
        "settled": sum(1 for p in projects if p.status in ("SETTLED", "CLOSED")),
    }
