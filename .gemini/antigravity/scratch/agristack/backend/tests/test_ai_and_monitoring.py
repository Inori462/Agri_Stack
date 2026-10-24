import io
import pytest
from fastapi.testclient import TestClient
from app.adapters.sentinel_adapter import Sentinel2Adapter
from app.adapters.opencv_adapter import OpenCVAdapter
from app.services.ai_prediction_service import AIPredictionService
from app.services.ai_assistant_service import AIAssistantService

def test_ml_yield_prediction(client: TestClient):
    # Register user to get token
    res = client.post("/api/v1/auth/register", json={
        "email": "ai.analyst@agristack.org",
        "phone_number": "+919833445566",
        "password": "Password123!",
        "full_name": "AI Analyst",
        "primary_role": "INVESTOR",
        "preferred_language": "en"
    })
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test Yield Prediction
    yield_res = client.post("/api/v1/predictions/yield", json={
        "crop": "Soybean",
        "acres": 10.0,
        "soil_type": "Black Cotton",
        "irrigation_source": "Drip",
        "season": "Kharif",
        "rainfall_mm": 950.0,
        "avg_temp_c": 28.0,
        "ndvi_index": 0.72,
        "soil_nitrogen": 280.0,
        "soil_phosphorus": 25.0
    }, headers=headers)
    assert yield_res.status_code == 200
    data = yield_res.json()
    assert data["predicted_yield_quintals"] > 0
    assert "confidence_range" in data
    assert "top_contributing_factors" in data
    assert "Acreage Scale Effect" in data["top_contributing_factors"]

def test_composite_risk_score_and_explainability(client: TestClient):
    # Test Low Risk
    low_risk = AIPredictionService.calculate_composite_risk_score(
        weather_variance_subscore=15,
        soil_deficit_subscore=20,
        crop_volatility_subscore=25,
        historical_yield_subscore=10,
        market_volatility_subscore=20
    )
    assert low_risk["composite_risk_score"] <= 35
    assert low_risk["risk_category"] == "LOW"
    assert len(low_risk["top_risk_contributors"]) == 5

    # Test High Risk
    high_risk = AIPredictionService.calculate_composite_risk_score(
        weather_variance_subscore=85,
        soil_deficit_subscore=70,
        crop_volatility_subscore=75,
        historical_yield_subscore=80,
        market_volatility_subscore=90
    )
    assert high_risk["composite_risk_score"] >= 66
    assert high_risk["risk_category"] == "HIGH"
    assert len(high_risk["mitigation_recommendations"]) > 0

def test_apmc_market_price_forecast(client: TestClient):
    price_info = AIPredictionService.forecast_market_price(
        crop="Soybean",
        harvest_month=10,
        rainfall_anomaly_pct=5.0
    )
    assert price_info["forecasted_price_per_quintal_inr"] > 1000.0
    assert price_info["forecasted_price_per_kg_inr"] == round(price_info["forecasted_price_per_quintal_inr"] / 100.0, 2)
    assert price_info["government_msp_per_quintal_inr"] == 4892.0
    assert price_info["price_trend"] in ["BULLISH", "STABLE", "BEARISH"]

def test_multilingual_ai_assistant():
    # English Query
    en_res = AIAssistantService.query_assistant(topic="crop", language="en")
    assert en_res["language"] == "en"
    assert "Soybean" in en_res["response"]["recommendation"]

    # Hindi Query
    hi_res = AIAssistantService.query_assistant(topic="schemes", language="hi", context_query="योजना")
    assert hi_res["language"] == "hi"
    assert "प्रधानमंत्री फसल बीमा योजना" in hi_res["response"]["schemes"][0]["name"]

    # Marathi Query
    mr_res = AIAssistantService.query_assistant(topic="schemes", language="mr", context_query="अनुदान")
    assert mr_res["language"] == "mr"
    assert "नानाजी देशमुख कृषी संजीवनी" in mr_res["response"]["schemes"][1]["name"]

def test_sentinel2_ndvi_calculation():
    # Standard formula verification: (NIR - Red) / (NIR + Red)
    ndvi = Sentinel2Adapter.calculate_ndvi(nir_band8=0.45, red_band4=0.15)
    # (0.45 - 0.15) / (0.45 + 0.15) = 0.30 / 0.60 = 0.50
    assert ndvi == 0.50

    # Telemetry simulation
    telemetry = Sentinel2Adapter.get_satellite_telemetry(center_lat=20.08, center_lng=73.98, crop_name="Soybean")
    assert "current_ndvi" in telemetry
    assert len(telemetry["historical_trajectory"]) == 6
    assert telemetry["health_status"] in ["POOR", "FAIR", "GOOD", "EXCELLENT"]

def test_opencv_crop_photo_verification():
    # Create synthetic image bytes
    dummy_image_bytes = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    analysis = OpenCVAdapter.analyze_crop_image(dummy_image_bytes)
    assert len(analysis["photo_sha256"]) == 64
    assert "is_sharp" in analysis
    assert "green_canopy_percentage" in analysis

    # Test Haversine Geotag distance check
    # 0 distance when identical
    geo_exact = OpenCVAdapter.verify_geotag(photo_lat=20.088, photo_lng=73.985, parcel_lat=20.088, parcel_lng=73.985)
    assert geo_exact["is_within_boundary"] is True
    assert geo_exact["distance_km"] == 0.0

    # Mismatch when photo is 100km away
    geo_far = OpenCVAdapter.verify_geotag(photo_lat=21.088, photo_lng=73.985, parcel_lat=20.088, parcel_lng=73.985)
    assert geo_far["is_within_boundary"] is False
    assert geo_far["status"] == "GEO_MISMATCH_SUSPICIOUS"
