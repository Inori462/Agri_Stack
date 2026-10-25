import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AgriStack"
    TAGLINE: str = "Smart Farms • Shared Growth • Sustainable Future"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Host
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security & Tokens
    SECRET_KEY: str = "agristack-super-secret-key-change-in-production-2026-secure-384bit"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # HMAC Peppers & Field Encryption Key (32 bytes url-safe base64 or hex)
    AADHAAR_PEPPER: str = "agristack-uidai-pepper-salt-987654321"
    PII_ENCRYPTION_KEY: str = "kZ8Qy0lPvH9t_1n3s8UuF4vB6rK9aW2cD5mE7xY0zQ4="
    
    # Database
    DATABASE_URL: str = "sqlite:///./agristack.db"
    # To use PostgreSQL in production, set e.g.:
    # DATABASE_URL: postgresql://agri:agri@localhost:5432/agristack
    
    
# CORS
BACKEND_CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://agri-stack-3245.onrender.com",
]

    # Razorpay (Sandbox / Pilot Mode)
    RAZORPAY_KEY_ID: str = "rzp_test_agristack_sandbox_key"
    RAZORPAY_KEY_SECRET: str = "rzp_test_secret_sample_key"
    RAZORPAY_WEBHOOK_SECRET: str = "whsec_agristack_webhook_signature_secret"
    RAZORPAY_SANDBOX: bool = True
    
    # Default Admin Seed Account
    FIRST_SUPERADMIN_EMAIL: str = "admin@agristack.org"
    FIRST_SUPERADMIN_PASSWORD: str = "AgriStack@Admin2026"
    FIRST_SUPERADMIN_PHONE: str = "+919800000001"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings()

def get_settings() -> Settings:
    return settings
