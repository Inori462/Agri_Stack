import uuid
from enum import Enum
from sqlalchemy import Column, String, Numeric, Integer, Date, ForeignKey, Text, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class ProjectStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_VERIFICATION = "UNDER_VERIFICATION"
    VERIFIED = "VERIFIED"
    OPEN_FOR_FUNDING = "OPEN_FOR_FUNDING"
    FUNDED = "FUNDED"
    IN_PROGRESS = "IN_PROGRESS"
    HARVESTED = "HARVESTED"
    SOLD = "SOLD"
    SETTLED = "SETTLED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"
    FLAGGED = "FLAGGED"

class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey("farms.id", ondelete="CASCADE"), nullable=False)
    parcel_id = Column(UUID(as_uuid=True), ForeignKey("land_parcels.id", ondelete="CASCADE"), nullable=False)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(200), nullable=False)
    crop_name = Column(String(100), nullable=False)
    crop_variety = Column(String(100), nullable=False)
    season = Column(String(50), nullable=False)  # Kharif, Rabi, Zaid
    
    sowing_date = Column(Date, nullable=False)
    estimated_harvest_date = Column(Date, nullable=False)
    
    # State Machine Status
    status = Column(String(50), default=ProjectStatus.DRAFT.value, nullable=False, index=True)
    
    # Financials & Digital Share Economics
    total_valuation_inr = Column(Numeric(12, 2), nullable=False)
    farmer_equity_percent = Column(Numeric(5, 2), default=30.00, nullable=False)
    investor_pool_percent = Column(Numeric(5, 2), default=70.00, nullable=False)
    total_shares = Column(Integer, default=100, nullable=False)
    share_price_inr = Column(Numeric(10, 2), nullable=False)
    funded_shares = Column(Integer, default=0, nullable=False)
    
    # Projections & Scoring
    expected_yield_quintals = Column(Numeric(10, 2), nullable=False)
    expected_revenue_inr = Column(Numeric(12, 2), nullable=False)
    risk_score = Column(Integer, default=0, nullable=False)  # 0 to 100
    
    # Relationships
    farm = relationship("Farm", back_populates="projects")
    parcel = relationship("LandParcel", back_populates="projects")
    farmer = relationship("User", foreign_keys=[farmer_id])
    
    state_logs = relationship("ProjectStateLog", back_populates="project", cascade="all, delete-orphan")
    share_holdings = relationship("ShareHolding", back_populates="project", cascade="all, delete-orphan")
    ownership_ledger_entries = relationship("OwnershipLedger", back_populates="project")
    escrow_milestones = relationship("EscrowMilestone", back_populates="project", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="project")
    farm_records = relationship("FarmRecord", back_populates="project")
    predictions = relationship("Prediction", back_populates="project")
    risk_evaluation = relationship("RiskScore", back_populates="project", uselist=False)
    marketplace_listings = relationship("MarketplaceListing", back_populates="project")
    sale_record = relationship("SaleRecord", back_populates="project", uselist=False)
    settlement = relationship("Settlement", back_populates="project", uselist=False)
    claims = relationship("CropFailureClaim", back_populates="project")

class ProjectStateLog(Base, TimestampMixin):
    __tablename__ = "project_state_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    from_state = Column(String(50), nullable=False)
    to_state = Column(String(50), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    rationale = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)

    project = relationship("Project", back_populates="state_logs")
