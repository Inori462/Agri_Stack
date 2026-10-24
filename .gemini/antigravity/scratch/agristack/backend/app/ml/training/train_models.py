import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

REGISTRY_DIR = os.path.join(os.path.dirname(__file__), "..", "model_registry", "v1")
os.makedirs(REGISTRY_DIR, exist_ok=True)

# Predefined agricultural distributions for Maharashtra & Indian cropping zones
CROPS = ["Soybean", "Cotton", "Wheat", "Onion", "Sugarcane", "Tur (Pigeon Pea)", "Gram (Chana)"]
SOIL_TYPES = ["Black Cotton", "Loamy", "Red", "Alluvial"]
IRRIGATION_TYPES = ["Drip", "Canal", "Borewell", "Rainfed"]
SEASONS = ["Kharif", "Rabi", "Zaid"]

def generate_synthetic_yield_dataset(n_samples: int = 2500) -> pd.DataFrame:
    """
    Generates realistic agronomic training data modeled after ICAR/DES agricultural statistics.
    Includes soil qualities, rainfall deviations, NDVI satellite vegetation index, and harvest quintals.
    """
    np.random.seed(42)
    crops = np.random.choice(CROPS, n_samples)
    soils = np.random.choice(SOIL_TYPES, n_samples)
    irrigations = np.random.choice(IRRIGATION_TYPES, n_samples)
    seasons = np.random.choice(SEASONS, n_samples)
    acres = np.random.uniform(1.0, 25.0, n_samples)
    rainfall_mm = np.random.uniform(400.0, 1600.0, n_samples)
    avg_temp_c = np.random.uniform(20.0, 38.0, n_samples)
    ndvi_index = np.random.uniform(0.30, 0.85, n_samples)
    soil_nitrogen_kg_ha = np.random.uniform(180.0, 360.0, n_samples)
    soil_phosphorus_kg_ha = np.random.uniform(12.0, 45.0, n_samples)

    # Base yield per acre in quintals per crop
    base_yield_per_acre = {
        "Soybean": 8.5,
        "Cotton": 7.0,
        "Wheat": 14.0,
        "Onion": 75.0,
        "Sugarcane": 320.0,
        "Tur (Pigeon Pea)": 6.0,
        "Gram (Chana)": 7.5
    }

    # Agronomic multipliers
    soil_mult = {"Black Cotton": 1.15, "Loamy": 1.10, "Alluvial": 1.12, "Red": 0.88}
    irr_mult = {"Drip": 1.25, "Canal": 1.10, "Borewell": 1.05, "Rainfed": 0.75}

    yields = []
    for c, s, irr, a, rain, ndvi in zip(crops, soils, irrigations, acres, rainfall_mm, ndvi_index):
        base = base_yield_per_acre[c] * a
        mult = soil_mult[s] * irr_mult[irr]
        ndvi_bonus = 0.7 + (ndvi * 0.5)
        rain_factor = 1.0 - abs(rain - 950.0) / 2200.0
        noise = np.random.normal(0, 0.05 * base)
        final_yield = max(1.0, round(base * mult * ndvi_bonus * rain_factor + noise, 2))
        yields.append(final_yield)

    df = pd.DataFrame({
        "crop": crops,
        "soil_type": soils,
        "irrigation_source": irrigations,
        "season": seasons,
        "acres": acres,
        "rainfall_mm": rainfall_mm,
        "avg_temp_c": avg_temp_c,
        "ndvi_index": ndvi_index,
        "soil_nitrogen": soil_nitrogen_kg_ha,
        "soil_phosphorus": soil_phosphorus_kg_ha,
        "yield_quintals": yields
    })
    return df

def generate_synthetic_price_dataset(n_samples: int = 2000) -> pd.DataFrame:
    """
    Generates historical APMC Mandi commodity market prices per quintal.
    """
    np.random.seed(101)
    crops = np.random.choice(CROPS, n_samples)
    months = np.random.randint(1, 13, n_samples)
    rainfall_anomaly_pct = np.random.uniform(-40.0, 40.0, n_samples)
    msp_support_inr = {
        "Soybean": 4892.0,
        "Cotton": 7121.0,
        "Wheat": 2275.0,
        "Onion": 1800.0,
        "Sugarcane": 340.0,
        "Tur (Pigeon Pea)": 7550.0,
        "Gram (Chana)": 5440.0
    }

    prices = []
    for c, m, rain_anom in zip(crops, months, rainfall_anomaly_pct):
        base_msp = msp_support_inr[c]
        # Scarcity premium when rainfall is deficient
        supply_shock = 1.0 - (rain_anom * 0.003)
        # Seasonal harvest arrival discount in peak harvest months
        harvest_dip = 0.92 if m in [10, 11, 12, 4] else 1.08
        noise = np.random.normal(0, 0.04 * base_msp)
        final_price = max(base_msp * 0.7, round(base_msp * supply_shock * harvest_dip + noise, 2))
        prices.append(final_price)

    df = pd.DataFrame({
        "crop": crops,
        "month": months,
        "rainfall_anomaly_pct": rainfall_anomaly_pct,
        "price_per_quintal_inr": prices
    })
    return df

def train_and_export_models():
    """Trains and serializes Yield Predictor and APMC Price Trend Predictor."""
    print("--- 1. Training Yield Prediction Model ---")
    df_yield = generate_synthetic_yield_dataset(3000)
    X_yield = df_yield.drop(columns=["yield_quintals"])
    y_yield = df_yield["yield_quintals"]

    categorical_features = ["crop", "soil_type", "irrigation_source", "season"]
    numerical_features = ["acres", "rainfall_mm", "avg_temp_c", "ndvi_index", "soil_nitrogen", "soil_phosphorus"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numerical_features)
        ]
    )

    yield_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X_yield, y_yield, test_size=0.2, random_state=42)
    yield_pipeline.fit(X_train, y_train)

    y_pred = yield_pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"Yield Model Evaluation: R^2 = {r2:.4f}, MAE = {mae:.2f} quintals, RMSE = {rmse:.2f} quintals")

    yield_model_path = os.path.join(REGISTRY_DIR, "yield_predictor_v1.joblib")
    joblib.dump(yield_pipeline, yield_model_path)
    print(f"Saved Yield Model to {yield_model_path}")

    print("\n--- 2. Training APMC Market Price Trend Model ---")
    df_price = generate_synthetic_price_dataset(2500)
    X_price = df_price.drop(columns=["price_per_quintal_inr"])
    y_price = df_price["price_per_quintal_inr"]

    price_preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["crop"]),
            ("num", "passthrough", ["month", "rainfall_anomaly_pct"])
        ]
    )

    price_pipeline = Pipeline([
        ("preprocessor", price_preprocessor),
        ("regressor", GradientBoostingRegressor(n_estimators=80, random_state=42))
    ])

    X_p_train, X_p_test, y_p_train, y_p_test = train_test_split(X_price, y_price, test_size=0.2, random_state=42)
    price_pipeline.fit(X_p_train, y_p_train)

    y_p_pred = price_pipeline.predict(X_p_test)
    p_r2 = r2_score(y_p_test, y_p_pred)
    p_mae = mean_absolute_error(y_p_test, y_p_pred)
    print(f"Price Model Evaluation: R^2 = {p_r2:.4f}, MAE = INR {p_mae:.2f} per quintal")

    price_model_path = os.path.join(REGISTRY_DIR, "price_forecaster_v1.joblib")
    joblib.dump(price_pipeline, price_model_path)
    print(f"Saved Price Model to {price_model_path}")

    # Metadata catalog
    metadata = {
        "version": "1.0.0",
        "trained_at": "2026-10-12T20:20:00Z",
        "yield_model": {
            "algorithm": "RandomForestRegressor(n_estimators=100)",
            "r2_score": round(r2, 4),
            "mae": round(mae, 2),
            "rmse": round(rmse, 2)
        },
        "price_model": {
            "algorithm": "GradientBoostingRegressor(n_estimators=80)",
            "r2_score": round(p_r2, 4),
            "mae": round(p_mae, 2)
        }
    }
    with open(os.path.join(REGISTRY_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    print("Exported model registry metadata.json.")

if __name__ == "__main__":
    train_and_export_models()
