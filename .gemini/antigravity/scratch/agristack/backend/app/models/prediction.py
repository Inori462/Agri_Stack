import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, JSON, DateTime
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class RiskCategory(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Prediction(Base, TimestampMixin):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    model_name = Column(String(100), nullable=False)
    predicted_yield_quintal = Column(Numeric(10, 2), nullable=False)
    predicted_revenue_inr = Column(Numeric(12, 2), nullable=False)
    confidence_pct = Column(Numeric(5, 2), nullable=False)
    
    # Explainable AI: Feature importance weights
    top_factors_json = Column(JSON, nullable=False)

    project = relationship("Project", back_populates="predictions")

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    composite_score = Column(Integer, nullable=False)  # 0 to 100
    risk_category = Column(String(20), default=RiskCategory.LOW.value, nullable=False)
    
    weather_subscore = Column(Integer, nullable=False)
    soil_subscore = Column(Integer, nullable=False)
    crop_subscore = Column(Integer, nullable=False)
    market_subscore = Column(Integer, nullable=False)
    historical_yield_subscore = Column(Integer, nullable=False)
    
    recommendations_json = Column(JSON, nullable=False)
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="risk_evaluation")
