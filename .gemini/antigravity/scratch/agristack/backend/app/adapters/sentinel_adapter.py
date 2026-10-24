from typing import Dict, Any, List
import math
import random
from datetime import datetime, timezone, timedelta

class Sentinel2Adapter:
    """
    Adapter for European Space Agency (ESA) Sentinel-2 satellite multi-spectral imagery.
    Computes Normalized Difference Vegetation Index (NDVI) and crop health time series.
    """

    @staticmethod
    def calculate_ndvi(nir_band8: float, red_band4: float) -> float:
        """
        Computes NDVI = (NIR - Red) / (NIR + Red).
        Returns value strictly bounded between -1.0 and +1.0.
        """
        denominator = nir_band8 + red_band4
        if denominator == 0:
            return 0.0
        ndvi = (nir_band8 - red_band4) / denominator
        return max(-1.0, min(1.0, round(ndvi, 3)))

    @staticmethod
    def classify_crop_health(ndvi: float) -> Dict[str, str]:
        """Maps NDVI value to agronomic vegetative health stage and color code."""
        if ndvi < 0.20:
            return {"category": "Barren / Sown (Bare Soil)", "status": "POOR", "color": "#ef4444"}
        elif ndvi < 0.40:
            return {"category": "Early Emergence / Germination", "status": "FAIR", "color": "#f59e0b"}
        elif ndvi < 0.60:
            return {"category": "Vegetative Growth (Healthy)", "status": "GOOD", "color": "#84cc16"}
        else:
            return {"category": "Peak Canopy / Flowering", "status": "EXCELLENT", "color": "#22c55e"}

    @staticmethod
    def get_satellite_telemetry(
        center_lat: float,
        center_lng: float,
        crop_name: str,
        days_since_sowing: int = 45
    ) -> Dict[str, Any]:
        """
        Simulates live Sentinel-2 satellite pass telemetry over the parcel boundary.
        Generates multispectral NIR/Red reflectances and historical 30-day NDVI trajectory.
        """
        # Crop phenology curve simulation
        peak_day = 65
        growth_ratio = min(1.0, days_since_sowing / peak_day)
        base_ndvi = 0.20 + (growth_ratio * 0.48) + random.uniform(-0.03, 0.04)
        current_ndvi = round(max(0.15, min(0.88, base_ndvi)), 3)

        # Reconstructed NIR (Band 8) and Red (Band 4) reflectances
        # Derived from NDVI = (NIR - Red) / (NIR + Red)
        # Setting Red = 0.12 (typical crop reflectance)
        red_band = 0.12
        nir_band = round(red_band * (1 + current_ndvi) / (1 - current_ndvi), 3)

        health_info = Sentinel2Adapter.classify_crop_health(current_ndvi)

        # 30-day time series trajectory
        now = datetime.now(timezone.utc)
        trajectory: List[Dict[str, Any]] = []
        for i in range(5, -1, -1):
            past_date = (now - timedelta(days=i * 5)).strftime("%Y-%m-%d")
            past_growth = max(0.1, (days_since_sowing - (i * 5)) / peak_day)
            past_val = round(max(0.18, min(0.85, 0.20 + (past_growth * 0.46))), 3)
            trajectory.append({
                "date": past_date,
                "ndvi": past_val,
                "cloud_cover_pct": round(random.uniform(1.0, 8.5), 1)
            })

        return {
            "center_coordinates": {"lat": center_lat, "lng": center_lng},
            "satellite_constellation": "Sentinel-2B",
            "tile_id": f"T43Q{abs(int(center_lat * 10)) % 90}",
            "last_overpass_utc": now.isoformat(),
            "cloud_cover_percentage": round(random.uniform(1.2, 5.0), 1),
            "nir_band_8_reflectance": nir_band,
            "red_band_4_reflectance": red_band,
            "current_ndvi": current_ndvi,
            "health_stage": health_info["category"],
            "health_status": health_info["status"],
            "health_color": health_info["color"],
            "historical_trajectory": trajectory
        }
