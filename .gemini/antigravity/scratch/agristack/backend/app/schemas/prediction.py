from typing import Dict, Any, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class PredictionResponse(BaseModel):
    id: UUID
    project_id: UUID
    model_name: str
    predicted_yield_quintal: float
    predicted_revenue_inr: float
    confidence_pct: float
    top_factors_json: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class RiskScoreResponse(BaseModel):
    id: UUID
    project_id: UUID
    composite_score: int
    risk_category: str
    weather_subscore: int
    soil_subscore: int
    crop_subscore: int
    market_subscore: int
    historical_yield_subscore: int
    recommendations_json: Dict[str, Any]
    evaluated_at: datetime

    class Config:
        from_attributes = True
