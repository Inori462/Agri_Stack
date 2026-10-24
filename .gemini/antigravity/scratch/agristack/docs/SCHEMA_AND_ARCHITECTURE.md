# AgriStack: Architectural Blueprint & Database Schema
**Tagline:** Smart Farms • Shared Growth • Sustainable Future  
**Version:** 1.0.0-Pilot  
**Security & Compliance Level:** High (SEBI CIS Sandbox Compliance, Aadhaar Masking, Cryptographic SHA-256 Ledger)

---

## 1. System Architecture Overview

AgriStack bridges traditional agricultural cultivation with modern financial digital ownership. A farm is modeled as an enterprise asset; each crop cycle is an operational cycle divided into digital fractional shares (e.g., 100 shares).

```
                                  +-----------------------------+
                                  |     React 18 + Tailwind     |
                                  |    PWA Frontend (EN/HI/MR)  |
                                  +--------------+--------------+
                                                 | HTTPS / WSS / REST
                                                 v
+-----------------------------------------------------------------------------------------------+
|                                    FastAPI Backend Gateway                                    |
|   +-------------------+  +-------------------+  +---------------------+  +----------------+   |
|   |   JWT + MFA RBAC  |  |  State Machine    |  | Cryptographic Hash  |  | Rate Limiter & |   |
|   |  Security Engine  |  |  Workflow Engine  |  |   Ledger Service    |  | Audit Logger   |   |
|   +-------------------+  +-------------------+  +---------------------+  +----------------+   |
+-----------------------------------------------------------------------------------------------+
         |                     |                       |                         |
         v                     v                       v                         v
+-----------------+   +------------------+   +-------------------+     +------------------+
|  PostgreSQL 15  |   | AI/ML Inference  |   | Sentinel-2 NDVI & |     | External Payment |
| Relational DB & |   |  scikit-learn /  |   | OpenCV Satellite  |     | & Verification   |
| Audit Ledger    |   |  XGBoost Engine  |   | Computer Vision   |     | Razorpay/DigiLocker
+-----------------+   +------------------+   +-------------------+     +------------------+
```

---

## 2. Directory Structure

```plaintext
agristack/
├── backend/
│   ├── alembic/                         # Database migration scripts
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI app entry point with middleware & routers
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py              # Login, Register, MFA (OTP/TOTP), Token refresh
│   │   │       ├── users.py             # User profile, role assignments, consent export
│   │   │       ├── kyc.py               # DigiLocker mock, Aadhaar masking, 7/12 Satbara upload
│   │   │       ├── farms.py             # Farm & Land Parcel registration with GeoJSON bounds
│   │   │       ├── projects.py          # Crop project lifecycle, state machine transitions
│   │   │       ├── shares.py            # Share issuance, shareholdings, cap-table
│   │   │       ├── investments.py       # Investor contracts, escrow backing, agreements
│   │   │       ├── payments.py          # Razorpay orders, webhook verification, escrow releases
│   │   │       ├── monitoring.py        # Weather, soil moisture, crop stage timeline
│   │   │       ├── predictions.py       # ML Yield, Market Price, Risk Score (0-100)
│   │   │       ├── marketplace.py       # Crop listing, buyers connect, harvest trade
│   │   │       ├── records.py           # Farm activity log, geotagged evidence, OpenCV checks
│   │   │       ├── ledger.py            # Append-only SHA-256 hash chain verification
│   │   │       ├── disputes.py          # Crop failure claims, insurance linkage, dispute queue
│   │   │       ├── notifications.py     # FCM push, email, SMS alerts
│   │   │       ├── reports.py           # Financial statements, P&L, investor ROI reports
│   │   │       ├── admin.py             # Verification queue, fraud flags, compliance reports
│   │   │       └── gov.py               # Anonymized public dashboard & district risk heatmaps
│   │   ├── core/
│   │   │   ├── config.py                # Pydantic BaseSettings, env configuration
│   │   │   ├── database.py              # SQLAlchemy engine, session maker, base model
│   │   │   ├── security.py              # Passlib bcrypt, pyjwt, AES-256 field encryption
│   │   │   ├── state_machine.py         # Strict Project State Machine validator
│   │   │   ├── exceptions.py            # Custom HTTP exceptions & structured JSON error handler
│   │   │   └── rate_limiter.py          # Slowapi / in-memory rate limiting
│   │   ├── models/                      # SQLAlchemy Declarative Models
│   │   │   ├── user.py                  # User, Role, UserRole, RefreshToken, MFASecret
│   │   │   ├── kyc.py                   # KYCRecord, SatbaraRecord, DigiLockerRef
│   │   │   ├── farm.py                  # Farm, LandParcel (GPS coordinates & Survey Number)
│   │   │   ├── project.py               # Project, ProjectStateLog, MilestoneEscrow
│   │   │   ├── share.py                 # ShareConfig, ShareHolding, OwnershipLedger
│   │   │   ├── investment.py            # InvestmentAgreement, EscrowMilestoneRelease
│   │   │   ├── payment.py               # PaymentTransaction, RazorpayWebhookEvent, Payout
│   │   │   ├── monitoring.py            # SensorWeatherData, SatelliteNdviLog, FarmRecord
│   │   │   ├── prediction.py            # YieldPrediction, RiskScore, ExplainabilityLog
│   │   │   ├── marketplace.py           # MarketplaceListing, SaleRecord, PriceAnomalyCheck
│   │   │   ├── dispute.py               # CropFailureClaim, DisputeRecord
│   │   │   ├── compliance.py            # ComplianceConsent, TermsRecord
│   │   │   └── audit.py                 # AuditLog, SecurityAlert
│   │   ├── schemas/                     # Pydantic Request/Response DTOs
│   │   ├── services/                    # Business Logic Layer
│   │   │   ├── auth_service.py
│   │   │   ├── kyc_service.py
│   │   │   ├── ledger_service.py        # SHA-256 hash chaining & cryptographic verification
│   │   │   ├── state_service.py         # State machine transition enforcement
│   │   │   ├── escrow_service.py        # Milestone-based fund unlocking (40% / 40% / 20%)
│   │   │   ├── ai_service.py            # Inference runner & explainable scoring
│   │   │   ├── settlement_service.py    # Pro-rata net profit/loss & dividend calculation
│   │   │   ├── notification_service.py
│   │   │   └── audit_service.py
│   │   ├── adapters/                    # External API integrations
│   │   │   ├── razorpay_adapter.py      # Razorpay payment orders & signature checks
│   │   │   ├── digilocker_adapter.py    # Mock/Sandbox Aadhaar & 7/12 land registry
│   │   │   ├── sentinel_adapter.py      # Sentinel-2 NDVI calculation & cloud mask
│   │   │   ├── weather_adapter.py       # Weather data provider
│   │   │   └── opencv_adapter.py        # Photo tampering, blur, and green-canopy analysis
│   │   └── ml/                          # Machine Learning models
│   │       ├── model_registry/
│   │       │   └── v1/                  # Serialized joblib/onnx models
│   │       └── training/
│   │           ├── train_yield_model.py
│   │           ├── train_risk_model.py
│   │           └── train_price_model.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_state_machine.py
│   │   ├── test_ledger_integrity.py
│   │   ├── test_escrow_settlement.py
│   │   └── test_ai_predictions.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   ├── locales/                     # en.json, hi.json, mr.json
│   │   ├── manifest.json                # PWA manifest
│   │   └── favicon.ico
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── common/                  # Buttons, Modals, Badges, AlertBanners
│   │   │   ├── layout/                  # Sidebar, Header, MobileNav, LanguageSwitcher
│   │   │   ├── maps/                    # Leaflet Farm Boundary drawer & NDVI overlay
│   │   │   ├── charts/                  # Share Donut, Yield Trend, Soil Sensor Line Chart
│   │   │   ├── wizard/                  # 3-Step Farmer Onboarding Wizard
│   │   │   └── ai/                      # AI Assistant Multilingual Drawer (Voice/Text)
│   │   ├── context/
│   │   │   ├── AuthContext.jsx          # User role, tokens, MFA status
│   │   │   ├── LanguageContext.jsx      # EN, HI, MR switcher with offline fallback
│   │   │   └── NotificationContext.jsx  # Toast alerts & FCM push listeners
│   │   ├── hooks/
│   │   ├── i18n/
│   │   ├── pages/
│   │   │   ├── Landing.jsx              # Platform introduction, Value prop, Pilot disclaimer
│   │   │   ├── Login.jsx & Register.jsx
│   │   │   ├── FarmerOnboarding.jsx     # Personal -> Land (7/12) -> DigiLocker Verification
│   │   │   ├── FarmerDashboard.jsx      # Farm overview, live status, business summaries
│   │   │   ├── CreateProject.jsx        # Crop cycle creation, budget, share division
│   │   │   ├── FarmMonitoring.jsx       # Sensor telemetry, NDVI satellite health, timeline
│   │   │   ├── AIInsights.jsx           # Yield forecasts, Explainable Risk Score, APMC price
│   │   │   ├── OwnershipShares.jsx      # Digital share cap table, donut chart, ledger history
│   │   │   ├── Marketplace.jsx          # Crop produce listings, verified buyer contact
│   │   │   ├── InvestorDiscovery.jsx    # Filter projects by crop, ROI, risk score (Low/Med/High)
│   │   │   ├── ProjectDetail.jsx        # Deep dive, milestones, Leaflet boundary, Invest CTA
│   │   │   ├── RecordsLedger.jsx        # Tamper-evident activity log & cryptographic proofs
│   │   │   ├── Reports.jsx              # P&L financial statements, harvest yields, tax summary
│   │   │   ├── AdminPanel.jsx           # KYC queue, land audit, flagged anomalies, disputes
│   │   │   └── GovSocietyDashboard.jsx  # Anonymized district risk heatmaps, income uplift
│   │   ├── services/                    # Axios API clients with auto-token refresh
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── infrastructure/
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   └── nginx.conf
│   └── github-actions/
│       └── ci-cd.yml
└── docs/
    ├── SCHEMA_AND_ARCHITECTURE.md
    └── LEGAL_AND_SEBI_COMPLIANCE.md
```

---

## 3. Database Schema Specification (PostgreSQL)

### 3.1. User, Role & Access Control (RBAC)

#### `users`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Primary email |
| `phone_number` | VARCHAR(20) | UNIQUE, NOT NULL | Mobile number (E.164 format) |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt salted hash |
| `full_name` | VARCHAR(150) | NOT NULL | Registered name |
| `primary_role` | VARCHAR(50) | NOT NULL | `FARMER`, `INVESTOR`, `ADMIN`, `GOV_OFFICER` |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active account state |
| `is_verified` | BOOLEAN | DEFAULT FALSE | Verified identity state |
| `mfa_enabled` | BOOLEAN | DEFAULT FALSE | Requires TOTP or SMS OTP |
| `mfa_secret` | VARCHAR(255) | NULLABLE | Encrypted TOTP secret |
| `preferred_language`| VARCHAR(10) | DEFAULT 'en' | `en`, `hi`, `mr` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Registration timestamp |
| `updated_at` | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

#### `roles` & `user_roles`
Supports fine-grained permissions: `FARMER`, `INVESTOR`, `ADMIN`, `GOV_OFFICER`.

---

### 3.2. KYC & Identity Verification (India-Specific)

#### `kyc_records`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Unique ID |
| `user_id` | UUID | REFERENCES users(id), UNIQUE | Linked user |
| `aadhaar_last4` | VARCHAR(4) | NOT NULL | Never store full 12 digits! Last 4 digits only |
| `aadhaar_hash` | VARCHAR(64) | NOT NULL | SHA-256 HMAC of full Aadhaar to prevent duplicate accounts |
| `pan_masked` | VARCHAR(10) | NULLABLE | Encrypted/Masked PAN for payout compliance |
| `digilocker_uri` | VARCHAR(255) | NULLABLE | Verification reference from DigiLocker API |
| `satbara_document_url`| VARCHAR(512) | NULLABLE | Uploaded 7/12 extract document (S3 presigned URL) |
| `verification_status` | VARCHAR(50) | DEFAULT 'SUBMITTED' | `SUBMITTED`, `AUTO_VERIFIED`, `MANUAL_REVIEW`, `VERIFIED`, `REJECTED` |
| `verified_by_admin_id`| UUID | REFERENCES users(id) | Admin reviewer |
| `rejection_reason` | TEXT | NULLABLE | Clarification for user |
| `verified_at` | TIMESTAMPTZ | NULLABLE | Verification timestamp |

---

### 3.3. Land Parcels & Farm Registration

#### `farms`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Farm ID |
| `farmer_id` | UUID | REFERENCES users(id), NOT NULL | Owning farmer |
| `farm_name` | VARCHAR(150) | NOT NULL | e.g., "Sahyadri Agro Estate" |
| `state` | VARCHAR(100) | NOT NULL | e.g., "Maharashtra" |
| `district` | VARCHAR(100) | NOT NULL | e.g., "Nashik" |
| `taluka` | VARCHAR(100) | NOT NULL | Sub-district |
| `village` | VARCHAR(100) | NOT NULL | Village name |
| `total_area_acres` | NUMERIC(10, 2) | NOT NULL | Total registered acreage |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Registration date |

#### `land_parcels`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Parcel ID |
| `farm_id` | UUID | REFERENCES farms(id), NOT NULL | Parent farm |
| `survey_number` | VARCHAR(100) | NOT NULL | Survey/Gat Number from 7/12 record |
| `sub_division_no` | VARCHAR(50) | NULLABLE | Hissa / sub-division |
| `center_latitude` | NUMERIC(10, 7) | NOT NULL | Farm GPS center latitude |
| `center_longitude`| NUMERIC(10, 7) | NOT NULL | Farm GPS center longitude |
| `boundary_geojson`| JSONB | NOT NULL | Polygons drawn on Leaflet map |
| `soil_type` | VARCHAR(100) | NOT NULL | Black Cotton, Loamy, Red, Alluvial |
| `irrigation_source`| VARCHAR(100)| NOT NULL | Drip, Canal, Borewell, Rainfed |
| `is_verified` | BOOLEAN | DEFAULT FALSE | Verified against 7/12 & satellite boundary |
| `duplicate_flag` | BOOLEAN | DEFAULT FALSE | Flagged if survey number exists under another user |

---

### 3.4. Project State Machine & Share Economics

#### Project State Machine
```
[DRAFT]
   │
   ▼ (submit)
[SUBMITTED] ──────────► [FLAGGED] (Anomaly / Duplicate survey / GPS mismatch)
   │                       ▲
   ▼ (verify KYC & Land)   │
[UNDER_VERIFICATION] ──────┘
   │
   ▼ (passed automated & admin check)
[VERIFIED]
   │
   ▼ (publish to investors)
[OPEN_FOR_FUNDING] ──────► [REJECTED]
   │
   ▼ (100% shares committed)
[FUNDED]
   │
   ▼ (sowing verified -> 40% escrow milestone released)
[IN_PROGRESS]
   │
   ▼ (harvest verified -> 20% milestone released)
[HARVESTED]
   │
   ▼ (sale invoice verified + buyer confirmation)
[SOLD]
   │
   ▼ (net profit distributed pro-rata)
[SETTLED]
   │
   ▼
[CLOSED]
```

#### `projects`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Project ID |
| `farm_id` | UUID | REFERENCES farms(id), NOT NULL | Farm location |
| `parcel_id` | UUID | REFERENCES land_parcels(id), NOT NULL | Parcel location |
| `farmer_id` | UUID | REFERENCES users(id), NOT NULL | Farmer enterprise owner |
| `title` | VARCHAR(200) | NOT NULL | e.g., "Organic Soybean & Tur Kharif 2026" |
| `crop_name` | VARCHAR(100) | NOT NULL | Soybean, Cotton, Wheat, Onion, Sugarcane |
| `variety` | VARCHAR(100) | NOT NULL | Certified Seed Variety (e.g., JS 335) |
| `season` | VARCHAR(50) | NOT NULL | Kharif / Rabi / Zaid |
| `sowing_date` | DATE | NOT NULL | Scheduled sowing date |
| `estimated_harvest_date` | DATE | NOT NULL | Expected maturity date |
| `status` | VARCHAR(50) | DEFAULT 'DRAFT' | State machine status |
| `total_valuation_inr` | NUMERIC(12, 2) | NOT NULL | Total capital budget |
| `farmer_equity_percent` | NUMERIC(5, 2) | DEFAULT 30.00 | Shares retained by farmer (e.g., 30%) |
| `investor_pool_percent` | NUMERIC(5, 2) | DEFAULT 70.00 | Shares available to public investors |
| `total_shares` | INTEGER | DEFAULT 100 | Fixed digital shares (e.g., 100 shares) |
| `share_price_inr` | NUMERIC(10, 2) | NOT NULL | `total_valuation_inr / total_shares` |
| `funded_shares` | INTEGER | DEFAULT 0 | Investor shares sold |
| `expected_yield_quintals` | NUMERIC(10, 2)| NOT NULL | Target yield |
| `expected_revenue_inr` | NUMERIC(12, 2)| NOT NULL | Target revenue |
| `risk_score` | INTEGER | DEFAULT 0 | 0–100 score (Low, Medium, High) |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Creation date |

#### `shares` & `share_holdings`
- `share_holdings`: records who owns what fraction:
  - `user_id` (UUID)
  - `project_id` (UUID)
  - `share_count` (INTEGER)
  - `share_percent` (NUMERIC(5, 2))
  - `investment_cost_inr` (NUMERIC(12, 2))
  - `holding_type` (`FARMER_EQUITY`, `INVESTOR_PURCHASE`)

---

### 3.5. Cryptographic Ownership Ledger (Tamper-Evident SHA-256 Hash Chain)

#### `ownership_ledger`
Each transaction is cryptographically linked to the previous transaction hash:  
`current_hash = SHA256(prev_hash + transaction_id + project_id + from_user + to_user + shares + amount + timestamp)`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `sequence_id` | BIGSERIAL | PRIMARY KEY | Monotonically increasing index |
| `entry_id` | UUID | UNIQUE, NOT NULL | Immutable entry identifier |
| `project_id` | UUID | REFERENCES projects(id), NOT NULL | Targeted farm project |
| `prev_hash` | VARCHAR(64) | NOT NULL | Hash of previous ledger entry (`0` for genesis) |
| `entry_hash` | VARCHAR(64) | NOT NULL | SHA-256 hash of this entry's serialized data |
| `transaction_type` | VARCHAR(50) | NOT NULL | `GENESIS_ISSUANCE`, `SHARE_PURCHASE`, `SECONDARY_TRANSFER`, `ESCROW_PAYOUT`, `SETTLEMENT_DISTRIBUTION` |
| `from_user_id` | UUID | NULLABLE (NULL for initial issuance) | Seller or Platform Escrow |
| `to_user_id` | UUID | REFERENCES users(id), NOT NULL | Buyer or Recipient |
| `shares_count` | INTEGER | NOT NULL | Number of shares transferred |
| `price_per_share_inr` | NUMERIC(10, 2) | NOT NULL | Price per share |
| `total_amount_inr` | NUMERIC(12, 2) | NOT NULL | Total transaction volume |
| `timestamp` | TIMESTAMPTZ | DEFAULT NOW() | Exact event timestamp |
| `signature` | VARCHAR(512) | NOT NULL | Server HMAC-SHA256 signature guaranteeing provenance |

*Integrity verification:* Any modification to past records invalidates all subsequent hashes, immediately detected by the `/api/v1/ledger/verify-integrity` audit endpoint.

---

### 3.6. Milestone Escrow & Payments

#### `escrow_milestones`
Funds collected from investors are not disbursed all at once. They are held in escrow and released according to verified milestones:
- **Milestone 1 (40%)**: Land preparation & verified sowing (seeds + fertilizer invoice + photo proof).
- **Milestone 2 (40%)**: Vegetative / Mid-cycle verified growth (NDVI satellite score > 0.45 + geotagged photos).
- **Milestone 3 (20%)**: Harvest verification (harvest photo, quintals recorded at weighbridge).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Milestone ID |
| `project_id` | UUID | REFERENCES projects(id) | Associated project |
| `milestone_index` | INTEGER | NOT NULL | 1, 2, 3 |
| `name` | VARCHAR(100) | NOT NULL | e.g., "Sowing Verification" |
| `percentage_release` | NUMERIC(5, 2) | NOT NULL | 40.00, 40.00, 20.00 |
| `amount_inr` | NUMERIC(12, 2) | NOT NULL | Release amount |
| `status` | VARCHAR(50) | DEFAULT 'LOCKED' | `LOCKED`, `SUBMITTED`, `VERIFIED`, `RELEASED`, `DISPUTED` |
| `proof_document_url` | VARCHAR(512) | NULLABLE | Uploaded proof |
| `verified_by_admin_id`| UUID | NULLABLE | Verifier |
| `released_at` | TIMESTAMPTZ | NULLABLE | Fund release timestamp |

#### `payments`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Payment ID |
| `user_id` | UUID | REFERENCES users(id) | Paying user |
| `project_id` | UUID | REFERENCES projects(id) | Target project |
| `razorpay_order_id` | VARCHAR(100) | UNIQUE, NOT NULL | Razorpay Order ID |
| `razorpay_payment_id` | VARCHAR(100) | UNIQUE, NULLABLE | Razorpay Payment ID |
| `razorpay_signature` | VARCHAR(255) | NULLABLE | Webhook / Client signature |
| `idempotency_key` | VARCHAR(128) | UNIQUE, NOT NULL | Prevents duplicate charge |
| `amount_inr` | NUMERIC(12, 2) | NOT NULL | Total amount |
| `currency` | VARCHAR(3) | DEFAULT 'INR' | Currency |
| `status` | VARCHAR(50) | DEFAULT 'CREATED' | `CREATED`, `AUTHORIZED`, `CAPTURED`, `FAILED`, `REFUNDED` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Timestamp |

---

### 3.7. Farm Monitoring, Sensors & Geotagged Records

#### `farm_records` (Tamper-Evident Activity Log)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Record ID |
| `project_id` | UUID | REFERENCES projects(id) | Project |
| `activity_type` | VARCHAR(100) | NOT NULL | `SOWING`, `IRRIGATION`, `FERTILIZER`, `PESTICIDE`, `HARVEST` |
| `activity_date` | DATE | NOT NULL | Date executed |
| `description` | TEXT | NOT NULL | Detailed action log |
| `evidence_photo_url` | VARCHAR(512) | NULLABLE | S3 photo URL |
| `photo_sha256` | VARCHAR(64) | NULLABLE | Hash of photo to prevent re-uploads |
| `geotag_lat` | NUMERIC(10, 7) | NULLABLE | Exif GPS latitude |
| `geotag_lng` | NUMERIC(10, 7) | NULLABLE | Exif GPS longitude |
| `opencv_score` | NUMERIC(5, 2) | NULLABLE | Image quality & green vegetation index |
| `verification_status`| VARCHAR(50) | DEFAULT 'VERIFIED'| `VERIFIED`, `FLAGGED`, `PENDING` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Record creation time |

#### `sensor_weather_data`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Reading ID |
| `parcel_id` | UUID | REFERENCES land_parcels(id) | Monitored parcel |
| `recorded_at` | TIMESTAMPTZ | NOT NULL | Timestamp of observation |
| `soil_moisture_pct`| NUMERIC(5, 2) | NOT NULL | Soil moisture (0–100%) |
| `soil_temp_c` | NUMERIC(5, 2) | NOT NULL | Soil temperature (°C) |
| `ambient_temp_c` | NUMERIC(5, 2) | NOT NULL | Ambient temperature (°C) |
| `humidity_pct` | NUMERIC(5, 2) | NOT NULL | Air humidity (%) |
| `rainfall_mm` | NUMERIC(6, 2) | NOT NULL | Precipitation (mm) |
| `ndvi_index` | NUMERIC(4, 3) | NOT NULL | Sentinel-2 NDVI (-1.000 to +1.000) |
| `source` | VARCHAR(50) | DEFAULT 'SIMULATED_IOT'| `IOT_DEVICE`, `WEATHER_API`, `SENTINEL_2` |

---

### 3.8. AI/ML Predictions & Risk Scoring

#### `predictions`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Prediction ID |
| `project_id` | UUID | REFERENCES projects(id) | Target project |
| `model_name` | VARCHAR(100) | NOT NULL | `yield_predictor_v1`, `price_forecaster_v1` |
| `predicted_yield_quintal` | NUMERIC(10, 2)| NOT NULL | Model yield estimate |
| `predicted_revenue_inr` | NUMERIC(12, 2)| NOT NULL | Model revenue estimate |
| `confidence_pct` | NUMERIC(5, 2) | NOT NULL | Prediction confidence |
| `top_factors_json` | JSONB | NOT NULL | Explainability features (e.g., rainfall, soil N-P-K) |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Inference timestamp |

#### `risk_scores`
Formula:
$$\text{Risk} = (0.25 \times \text{WeatherVar}) + (0.20 \times \text{SoilDeficit}) + (0.20 \times \text{CropVolatility}) + (0.15 \times \text{YieldHistory}) + (0.20 \times \text{MarketVolatility})$$
- 0–35: **LOW RISK**
- 36–65: **MEDIUM RISK**
- 66–100: **HIGH RISK**

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Score ID |
| `project_id` | UUID | REFERENCES projects(id), UNIQUE | Evaluated project |
| `composite_score` | INTEGER | NOT NULL | 0 to 100 |
| `risk_category` | VARCHAR(20) | NOT NULL | `LOW`, `MEDIUM`, `HIGH` |
| `weather_subscore` | INTEGER | NOT NULL | 0–100 sub-score |
| `soil_subscore` | INTEGER | NOT NULL | 0–100 sub-score |
| `crop_subscore` | INTEGER | NOT NULL | 0–100 sub-score |
| `market_subscore` | INTEGER | NOT NULL | 0–100 sub-score |
| `recommendations` | JSONB | NOT NULL | Mitigation strategies & schemes |
| `evaluated_at` | TIMESTAMPTZ | DEFAULT NOW() | Evaluation time |

---

### 3.9. Marketplace, Harvest Sales & APMC Price Verification

#### `marketplace_listings`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Listing ID |
| `project_id` | UUID | REFERENCES projects(id) | Source farm project |
| `crop_name` | VARCHAR(100) | NOT NULL | Produce name |
| `quantity_kg` | NUMERIC(10, 2) | NOT NULL | Total available quantity in kg |
| `price_per_kg_inr` | NUMERIC(8, 2) | NOT NULL | Asked price |
| `status` | VARCHAR(50) | DEFAULT 'ACTIVE' | `ACTIVE`, `NEGOTIATING`, `SOLD` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Listing date |

#### `sale_records`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Record ID |
| `project_id` | UUID | REFERENCES projects(id) | Project |
| `buyer_name` | VARCHAR(150) | NOT NULL | Institutional buyer or trader name |
| `buyer_contact` | VARCHAR(20) | NOT NULL | Phone / Email |
| `quantity_sold_kg` | NUMERIC(10, 2) | NOT NULL | Weight sold |
| `price_per_kg_inr` | NUMERIC(8, 2) | NOT NULL | Realized price per kg |
| `gross_revenue_inr`| NUMERIC(12, 2) | NOT NULL | `quantity_sold_kg * price_per_kg_inr` |
| `buyer_otp_verified`| BOOLEAN | DEFAULT FALSE | Buyer verified sale via OTP |
| `apmc_modal_price` | NUMERIC(8, 2) | NOT NULL | APMC Market benchmark price |
| `price_anomaly_flag`| BOOLEAN | DEFAULT FALSE | True if sold price deviates >25% from APMC modal |
| `invoice_url` | VARCHAR(512) | NOT NULL | Signed weighbridge/buyer invoice |
| `verified_at` | TIMESTAMPTZ | NULLABLE | Admin/System verification time |

---

### 3.10. Returns, Settlement & Pro-Rata Distribution

#### `settlements`
Calculates final farm economics:
$$\text{Net Distributable} = \text{Gross Revenue} - \text{Cultivation Costs} - \text{Platform Fee (5\%)} + \text{Insurance Payout}$$
- If positive: Distributed pro-rata according to share percentage (e.g. 1 share of 100 = 1% of net profit).
- If negative (Loss): Loss absorbed pro-rata; remaining escrow funds and insurance claims applied first.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Settlement ID |
| `project_id` | UUID | REFERENCES projects(id), UNIQUE | Project |
| `gross_revenue_inr`| NUMERIC(12, 2) | NOT NULL | Total realized revenue |
| `actual_expenses_inr`| NUMERIC(12, 2)| NOT NULL | Verified production cost |
| `platform_fee_inr` | NUMERIC(12, 2) | NOT NULL | 5% AgriStack maintenance fee |
| `insurance_recovered_inr`| NUMERIC(12, 2)| DEFAULT 0.00 | Payout from PMFBY or weather insurance |
| `net_distributable_inr` | NUMERIC(12, 2)| NOT NULL | Net profit or loss |
| `is_profit` | BOOLEAN | NOT NULL | True if net > 0 |
| `per_share_return_inr` | NUMERIC(10, 2) | NOT NULL | Dividend or loss per share |
| `status` | VARCHAR(50) | DEFAULT 'COMPLETED' | `CALCULATED`, `DISBURSING`, `COMPLETED` |
| `settled_at` | TIMESTAMPTZ | DEFAULT NOW() | Completion date |

#### `investor_payouts`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Payout ID |
| `settlement_id` | UUID | REFERENCES settlements(id) | Associated settlement |
| `user_id` | UUID | REFERENCES users(id) | Investor |
| `shares_held` | INTEGER | NOT NULL | Number of shares held |
| `payout_amount_inr`| NUMERIC(12, 2) | NOT NULL | Bank credit amount |
| `bank_ref_number` | VARCHAR(100) | NULLABLE | UTR / IMPS ref from Razorpay Payouts |
| `status` | VARCHAR(50) | DEFAULT 'INITIATED' | `INITIATED`, `PROCESSED`, `FAILED` |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Timestamp |

---

### 3.11. Failure Claims, Disputes & Insurance

#### `crop_failure_claims`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Claim ID |
| `project_id` | UUID | REFERENCES projects(id) | Project |
| `farmer_id` | UUID | REFERENCES users(id) | Farmer claimant |
| `cause` | VARCHAR(100) | NOT NULL | `UNSEASONAL_RAINFALL`, `DROUGHT`, `HAILSTORM`, `PEST_ATTACK` |
| `estimated_damage_pct`| NUMERIC(5, 2)| NOT NULL | Reported % loss |
| `insurance_policy_number`| VARCHAR(100)| NULLABLE | Pradhan Mantri Fasal Bima Yojana (PMFBY) ref |
| `evidence_photos` | JSONB | NOT NULL | Photo links & drone survey refs |
| `admin_review_status` | VARCHAR(50) | DEFAULT 'PENDING' | `PENDING`, `INVESTIGATION`, `APPROVED`, `REJECTED` |
| `insurance_settlement_inr`| NUMERIC(12, 2)| DEFAULT 0.00 | Claim received from insurer |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Claim filing date |

---

### 3.12. Audit Logs & Compliance Consents

#### `audit_logs`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | BIGSERIAL | PRIMARY KEY | Sequential ID |
| `actor_id` | UUID | NULLABLE | User who performed the action |
| `actor_role` | VARCHAR(50) | NOT NULL | Role at time of action |
| `action` | VARCHAR(100) | NOT NULL | `LOGIN`, `KYC_APPROVAL`, `PROJECT_STATUS_CHANGE`, `SHARE_PURCHASE`, `ESCROW_RELEASE` |
| `resource_type` | VARCHAR(100) | NOT NULL | `PROJECT`, `SHARE`, `PAYMENT`, `LAND_PARCEL` |
| `resource_id` | VARCHAR(100) | NOT NULL | Entity ID |
| `ip_address` | VARCHAR(45) | NOT NULL | Client IP (IPv4 or IPv6) |
| `user_agent` | VARCHAR(255) | NOT NULL | Browser / Client User-Agent |
| `details` | JSONB | NOT NULL | State change diff (before/after) |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW() | Immutable timestamp |

#### `compliance_consents`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | Consent ID |
| `user_id` | UUID | REFERENCES users(id) | User |
| `consent_type` | VARCHAR(100) | NOT NULL | `SEBI_PILOT_SANDBOX_ACK`, `DIGILOCKER_PULL_CONSENT`, `TERMS_OF_SERVICE` |
| `version` | VARCHAR(20) | NOT NULL | Legal document version (e.g., "1.0") |
| `ip_address` | VARCHAR(45) | NOT NULL | IP of user when consent signed |
| `agreed_at` | TIMESTAMPTZ | DEFAULT NOW() | Timestamp of agreement |

---

## 4. Key Architectural Patterns & Guarantees

1. **Strict State Machine**: Status transitions in `projects` cannot skip stages (e.g. `DRAFT` cannot go directly to `FUNDED`). Every transition generates an immutable record in `project_state_logs`.
2. **Double-Hashed KYC Privacy**:
   - Never store plain 12-digit Aadhaar.
   - Store only last 4 digits for visual verification (`xxxx-xxxx-1234`).
   - Store SHA-256 HMAC of full Aadhaar with a server pepper key to detect duplicate account creation attempts.
3. **Cryptographic SHA-256 Ownership Ledger**:
   - Each share issuance or purchase references `prev_hash`.
   - Prevents database tampering or silent manipulation of cap-tables.
4. **Milestone Escrow Security**:
   - 40% (Sowing) -> 40% (Mid-cycle satellite NDVI verification) -> 20% (Harvest).
   - Farmer only unlocks funds as verified milestones are achieved.
5. **Explainable AI**:
   - Yield & risk predictions return top contributing feature weights (e.g., rainfall deviation, soil organic carbon, market price variance) so farmers and investors understand the "why".
6. **Pilot / Sandbox Compliance**:
   - Platform operates with test Razorpay keys and clear legal disclaimers stating that fractional agricultural projects operate under sandbox guidelines awaiting official SEBI/agricultural collective investment formalization.
