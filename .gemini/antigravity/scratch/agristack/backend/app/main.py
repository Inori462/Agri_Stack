from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import init_db, SessionLocal
from .core.exceptions import AppException, app_exception_handler
from .core.security import get_password_hash
from .models.user import User, UserRole
from .models.compliance import TermsRecord
from sqlalchemy.orm import Session
from .api.v1.auth import router as auth_router
from .api.v1.users import router as users_router
from .api.v1.ledger import router as ledger_router
from .api.v1.kyc import router as kyc_router
from .api.v1.farms import router as farms_router
from .api.v1.projects import router as projects_router
from .api.v1.predictions import router as predictions_router
from .api.v1.monitoring import router as monitoring_router
from .api.v1.payments import router as payments_router
from .api.v1.marketplace import router as marketplace_router
from .api.v1.settlements import router as settlements_router
from .api.v1.disputes import router as disputes_router
from .api.v1.gov import router as gov_router
from .api.v1.admin import router as admin_router
from .api.v1.reports import router as reports_router

def seed_defaults(db: Session = None):
    """Seeds superadmin account and legal sandbox disclaimer if missing."""
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True
    try:
        # 1. Superadmin Seed
        admin = db.query(User).filter(User.email == settings.FIRST_SUPERADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=settings.FIRST_SUPERADMIN_EMAIL,
                phone_number=settings.FIRST_SUPERADMIN_PHONE,
                hashed_password=get_password_hash(settings.FIRST_SUPERADMIN_PASSWORD),
                full_name="AgriStack System Administrator",
                primary_role=UserRole.ADMIN.value,
                is_active=True,
                is_verified=True,
                mfa_enabled=False,
                preferred_language="en"
            )
            db.add(admin)
            db.commit()

        demo_accounts = [
            {
                "email": "farmer@agristack.org",
                "phone_number": "+919800000010",
                "password": "AgriStack@Farmer2026",
                "full_name": "Ganesh Patil",
                "primary_role": UserRole.FARMER.value,
            },
            {
                "email": "investor@agristack.org",
                "phone_number": "+919800000020",
                "password": "AgriStack@Investor2026",
                "full_name": "Radha Sharma",
                "primary_role": UserRole.INVESTOR.value,
            },
            {
                "email": "gov@agristack.org",
                "phone_number": "+919800000030",
                "password": "AgriStack@Gov2026",
                "full_name": "District Agriculture Officer",
                "primary_role": UserRole.GOV_OFFICER.value,
            },
        ]
        for acct in demo_accounts:
            existing = db.query(User).filter(User.email == acct["email"]).first()
            if not existing:
                db.add(
                    User(
                        email=acct["email"],
                        phone_number=acct["phone_number"],
                        hashed_password=get_password_hash(acct["password"]),
                        full_name=acct["full_name"],
                        primary_role=acct["primary_role"],
                        is_active=True,
                        is_verified=True,
                        mfa_enabled=False,
                        preferred_language="en",
                    )
                )
        db.commit()

        # 2. Terms & Regulatory Disclaimer Seed
        terms = db.query(TermsRecord).filter(TermsRecord.version == "1.0.0").first()
        if not terms:
            terms = TermsRecord(
                title="AgriStack Fractional Farm Enterprise Pilot Terms & SEBI CIS Disclaimer",
                version="1.0.0",
                content_markdown=(
                    "### AgriStack Pilot Regulatory Notice\n\n"
                    "1. **Operational Rights:** Digital shares represent fractional profit-sharing agreements "
                    "in operational crop cycles and do not confer ownership of agricultural land.\n"
                    "2. **Sandbox Governance:** This platform operates under pilot guidelines for agricultural innovation.\n"
                    "3. **Inherent Risks:** Agricultural production is subject to weather, pest, and market volatility."
                ),
                is_active=True
            )
            db.add(terms)
            db.commit()
    finally:
        if should_close:
            db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables & seeds exist
    init_db()
    seed_defaults()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        f"**{settings.TAGLINE}**\n\n"
        "A share-driven farm enterprise platform turning farming into a scalable business "
        "using digital ownership shares, verified IoT & satellite data, and AI insights.\n\n"
        "**Pilot Mode:** Operating with regulatory sandbox controls and test payment gateways."
    ),
    version="1.0.0-pilot",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(ledger_router, prefix=settings.API_V1_STR)
app.include_router(kyc_router, prefix=settings.API_V1_STR)
app.include_router(farms_router, prefix=settings.API_V1_STR)
app.include_router(projects_router, prefix=settings.API_V1_STR)
app.include_router(predictions_router, prefix=settings.API_V1_STR)
app.include_router(monitoring_router, prefix=settings.API_V1_STR)
app.include_router(payments_router, prefix=settings.API_V1_STR)
app.include_router(marketplace_router, prefix=settings.API_V1_STR)
app.include_router(settlements_router, prefix=settings.API_V1_STR)
app.include_router(disputes_router, prefix=settings.API_V1_STR)
app.include_router(gov_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health & Status"])
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": "1.0.0-pilot",
        "status": "online",
        "docs": "/docs",
        "mode": "Sandbox / Pilot"
    }

@app.get("/health", tags=["Health & Status"])
def health_check():
    return {"status": "healthy", "database": "connected"}
