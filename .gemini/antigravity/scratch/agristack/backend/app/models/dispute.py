import uuid
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional, List
from sqlalchemy import Column, String, Numeric, Date, ForeignKey, JSON, Text, DateTime
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class ClaimStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    INSPECTION_SCHEDULED = "INSPECTION_SCHEDULED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class CropFailureClaim(Base, TimestampMixin):
    __tablename__ = "crop_failure_claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    incident_type = Column(String(100), nullable=True)  # UNSEASONAL_RAINFALL, DROUGHT, HAILSTORM, PEST_ATTACK
    failure_reason = Column(String(200), nullable=True)
    incident_date = Column(Date, default=date.today, nullable=True)
    estimated_damage_pct = Column(Numeric(5, 2), nullable=True)
    affected_area_pct = Column(Numeric(5, 2), nullable=True)
    
    insurance_policy_no = Column(String(100), nullable=True)
    insurance_policy_number = Column(String(100), nullable=True)
    evidence_photos = Column(JSON, default=list, nullable=True)
    evidence_urls = Column(JSON, default=list, nullable=True)
    
    admin_status = Column(String(50), default=ClaimStatus.PENDING.value, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)
    approved_insurance_amount_inr = Column(Numeric(12, 2), default=0.00, nullable=True)
    insurance_approved_amount = Column(Numeric(12, 2), default=0.00, nullable=True)
    refund_pool_amount_inr = Column(Numeric(12, 2), default=0.00, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="claims")
    farmer = relationship("User", foreign_keys=[farmer_id])

    def __init__(self, **kwargs):
        if "failure_reason" in kwargs and "incident_type" not in kwargs:
            kwargs["incident_type"] = kwargs["failure_reason"]
        elif "incident_type" in kwargs and "failure_reason" not in kwargs:
            kwargs["failure_reason"] = kwargs["incident_type"]

        if "affected_area_pct" in kwargs and "estimated_damage_pct" not in kwargs:
            kwargs["estimated_damage_pct"] = kwargs["affected_area_pct"]
        elif "estimated_damage_pct" in kwargs and "affected_area_pct" not in kwargs:
            kwargs["affected_area_pct"] = kwargs["estimated_damage_pct"]

        if "insurance_policy_number" in kwargs and "insurance_policy_no" not in kwargs:
            kwargs["insurance_policy_no"] = kwargs["insurance_policy_number"]
        elif "insurance_policy_no" in kwargs and "insurance_policy_number" not in kwargs:
            kwargs["insurance_policy_number"] = kwargs["insurance_policy_no"]

        if "evidence_urls" in kwargs and "evidence_photos" not in kwargs:
            kwargs["evidence_photos"] = kwargs["evidence_urls"]
        elif "evidence_photos" in kwargs and "evidence_urls" not in kwargs:
            kwargs["evidence_urls"] = kwargs["evidence_photos"]

        if "status" in kwargs and "admin_status" not in kwargs:
            kwargs["admin_status"] = kwargs["status"]
        elif "admin_status" in kwargs and "status" not in kwargs:
            kwargs["status"] = kwargs["admin_status"]

        if "insurance_approved_amount" in kwargs and "approved_insurance_amount_inr" not in kwargs:
            kwargs["approved_insurance_amount_inr"] = kwargs["insurance_approved_amount"]
        elif "approved_insurance_amount_inr" in kwargs and "insurance_approved_amount" not in kwargs:
            kwargs["insurance_approved_amount"] = kwargs["approved_insurance_amount_inr"]

        if "admin_notes" in kwargs and "resolution_notes" not in kwargs:
            kwargs["resolution_notes"] = kwargs["admin_notes"]
        elif "resolution_notes" in kwargs and "admin_notes" not in kwargs:
            kwargs["admin_notes"] = kwargs["resolution_notes"]

        super().__init__(**kwargs)

class DisputeRecord(Base, TimestampMixin):
    __tablename__ = "dispute_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    raised_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    raised_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    against_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    dispute_category = Column(String(100), nullable=True)
    dispute_type = Column(String(100), nullable=True)
    claim_details = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    evidence_urls = Column(JSON, default=list, nullable=True)
    
    status = Column(String(50), default="OPEN", nullable=False)  # OPEN, UNDER_REVIEW, RESOLVED, ESCALATED
    resolution = Column(String(200), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    resolved_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    def __init__(self, **kwargs):
        if "raised_by" in kwargs and "raised_by_user_id" not in kwargs:
            kwargs["raised_by_user_id"] = kwargs["raised_by"]
        elif "raised_by_user_id" in kwargs and "raised_by" not in kwargs:
            kwargs["raised_by"] = kwargs["raised_by_user_id"]

        if "dispute_type" in kwargs and "dispute_category" not in kwargs:
            kwargs["dispute_category"] = kwargs["dispute_type"]
        elif "dispute_category" in kwargs and "dispute_type" not in kwargs:
            kwargs["dispute_type"] = kwargs["dispute_category"]

        if "description" in kwargs and "claim_details" not in kwargs:
            kwargs["claim_details"] = kwargs["description"]
        elif "claim_details" in kwargs and "description" not in kwargs:
            kwargs["description"] = kwargs["claim_details"]

        if "resolved_by" in kwargs and "resolved_by_admin_id" not in kwargs:
            kwargs["resolved_by_admin_id"] = kwargs["resolved_by"]
        elif "resolved_by_admin_id" in kwargs and "resolved_by" not in kwargs:
            kwargs["resolved_by"] = kwargs["resolved_by_admin_id"]

        super().__init__(**kwargs)
