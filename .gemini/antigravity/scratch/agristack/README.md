# AgriStack

**Smart Farms • Shared Growth • Sustainable Future**

Pilot platform for fractional crop-cycle enterprises in Maharashtra. Digital shares represent operational profit-sharing rights, not land titles. Operates in a SEBI CIS sandbox-style control set with Razorpay test payments, Aadhaar HMAC masking, and a SHA-256 ownership ledger.

## What is in this repo

| Phase | Status |
| --- | --- |
| 1 Architecture & schema | Complete |
| 2 Auth, JWT, MFA, encryption | Complete |
| 3 Onboarding, GeoJSON parcels, 100-share projects, 40/40/20 escrow | Complete |
| 4 Yield / APMC / risk models, NDVI, OpenCV, EN/HI/MR assistant | Complete |
| 5 Razorpay, marketplace, APMC anomaly, pro-rata settlement, insurance claims | Complete |
| 6 React + Tailwind PWA (14+ pages, AI drawer) | Complete |
| 7 Demo seed, Docker, GitHub Actions, README | Complete |

## Demo accounts (seeded on API start)

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@agristack.org` | `AgriStack@Admin2026` |
| Farmer | `farmer@agristack.org` | `AgriStack@Farmer2026` |
| Investor | `investor@agristack.org` | `AgriStack@Investor2026` |
| Gov officer | `gov@agristack.org` | `AgriStack@Gov2026` |

## Local development

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend PWA

```bash
cd frontend
npm install
npm run dev
```

UI: http://localhost:3000 (Vite proxies `/api` to the FastAPI gateway).

### Tests

```bash
python -m pytest -q
```

## Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend: http://localhost:8000  
- Postgres: `postgresql://agri:agri@localhost:5432/agristack`

## Settlement formula

`Net distributable = Gross revenue − Expenses − 5% platform fee + Insurance recovered`

Investor pool = `100% − farmer equity %`. Each investor is paid pro-rata on shares held. Admin marks UTR transfer on `/api/v1/settlements/payouts/{id}/transfer`.

## Payments (sandbox)

Razorpay order + HMAC signature verification. Automated tests and the PWA checkout accept signatures prefixed with `test_sig_`. Webhooks accept `X-Razorpay-Signature` values prefixed with `test_` when `RAZORPAY_SANDBOX=true`.

## Compliance

See `docs/LEGAL_AND_SEBI_COMPLIANCE.md` and `docs/SCHEMA_AND_ARCHITECTURE.md`. Full Aadhaar is never stored; last-4 + HMAC only.

## CI

`.github/workflows/ci.yml` runs backend pytest and a frontend production build on push/PR.
