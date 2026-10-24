from typing import Optional
from fastapi import APIRouter, Depends, Query, Body
from pydantic import BaseModel, Field
from ...core.dependencies import get_current_user
from ...models.user import User
from ...services.ai_prediction_service import AIPredictionService
from ...services.ai_assistant_service import AIAssistantService

router = APIRouter(prefix="/predictions", tags=["AI/ML Analytics & Predictions"])

class YieldPredictionInput(BaseModel):
    crop: str = Field(default="Soybean", description="Target crop")
    acres: float = Field(default=5.0, gt=0)
    soil_type: str = Field(default="Black Cotton", description="Black Cotton, Loamy, Red, Alluvial")
    irrigation_source: str = Field(default="Drip", description="Drip, Canal, Borewell, Rainfed")
    season: str = Field(default="Kharif")
    rainfall_mm: float = Field(default=920.0, gt=0)
    avg_temp_c: float = Field(default=28.5)
    ndvi_index: float = Field(default=0.65, ge=-1.0, le=1.0)
    soil_nitrogen: float = Field(default=240.0)
    soil_phosphorus: float = Field(default=22.0)

class RiskScoreInput(BaseModel):
    weather_variance_subscore: int = Field(default=25, ge=0, le=100)
    soil_deficit_subscore: int = Field(default=20, ge=0, le=100)
    crop_volatility_subscore: int = Field(default=30, ge=0, le=100)
    historical_yield_subscore: int = Field(default=15, ge=0, le=100)
    market_volatility_subscore: int = Field(default=25, ge=0, le=100)

class PriceForecastInput(BaseModel):
    crop: str = Field(default="Soybean")
    harvest_month: int = Field(default=10, ge=1, le=12)
    rainfall_anomaly_pct: float = Field(default=0.0)

class AIAssistantInput(BaseModel):
    topic: str = Field(default="crop", description="crop or schemes")
    language: str = Field(default="en", description="en, hi, mr")
    query_text: str = Field(default="")

@router.post("/yield")
def predict_crop_yield(
    req: YieldPredictionInput,
    current_user: User = Depends(get_current_user)
):
    """Predicts expected harvest yield in quintals with explainable top feature factors."""
    return AIPredictionService.predict_yield(
        crop=req.crop,
        acres=req.acres,
        soil_type=req.soil_type,
        irrigation_source=req.irrigation_source,
        season=req.season,
        rainfall_mm=req.rainfall_mm,
        avg_temp_c=req.avg_temp_c,
        ndvi_index=req.ndvi_index,
        soil_nitrogen=req.soil_nitrogen,
        soil_phosphorus=req.soil_phosphorus
    )

@router.post("/risk-score")
def calculate_risk_score(
    req: RiskScoreInput,
    current_user: User = Depends(get_current_user)
):
    """Calculates standardized 0–100 composite risk score (LOW/MEDIUM/HIGH) and breakdown."""
    return AIPredictionService.calculate_composite_risk_score(
        weather_variance_subscore=req.weather_variance_subscore,
        soil_deficit_subscore=req.soil_deficit_subscore,
        crop_volatility_subscore=req.crop_volatility_subscore,
        historical_yield_subscore=req.historical_yield_subscore,
        market_volatility_subscore=req.market_volatility_subscore
    )

@router.post("/market-price")
def forecast_market_price(
    req: PriceForecastInput,
    current_user: User = Depends(get_current_user)
):
    """Forecasts APMC Mandi commodity price per quintal and per kg at harvest time."""
    return AIPredictionService.forecast_market_price(
        crop=req.crop,
        harvest_month=req.harvest_month,
        rainfall_anomaly_pct=req.rainfall_anomaly_pct
    )

@router.post("/ai-assistant")
def consult_ai_assistant(
    req: AIAssistantInput,
    current_user: User = Depends(get_current_user)
):
    """Multilingual AI Assistant providing expert agronomic & scheme advice in EN, HI, or MR."""
    return AIAssistantService.query_assistant(
        topic=req.topic,
        language=req.language or current_user.preferred_language,
        context_query=req.query_text
    )
