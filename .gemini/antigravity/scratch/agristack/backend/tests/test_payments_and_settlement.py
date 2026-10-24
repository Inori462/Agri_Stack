import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.models.project import Project, ProjectStatus
from app.models.share import ShareHolding, HoldingType
from app.core.database import SessionLocal

def create_seeded_farmer_and_project(client: TestClient):
    """Helper fixture to set up a verified farmer, farm parcel, and funded/active project."""
    # 1. Register Farmer
    farmer_reg = client.post("/api/v1/auth/register", json={
        "email": "ganesh.farmer@agristack.org",
        "phone_number": "+919877001122",
        "password": "SecurePassword2026!",
        "full_name": "Ganesh Shinde",
        "primary_role": "FARMER",
        "preferred_language": "mr"
    })
    assert farmer_reg.status_code == 201
    farmer_token = farmer_reg.json()["access_token"]
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}

    # 2. Login Admin
    admin_login = client.post("/api/v1/auth/login", json={
        "email_or_phone": "admin@agristack.org",
        "password": "AgriStack@Admin2026"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Complete KYC
    kyc_res = client.post("/api/v1/kyc/submit", json={
        "aadhaar_number": "123456789012",
        "pan_number": "ABCDE9876Z",
        "satbara_document_url": "https://s3.amazonaws.com/agristack/satbara_ganesh.pdf",
        "survey_number_claimed": "205/B"
    }, headers=farmer_headers)
    assert kyc_res.status_code == 200
    kyc_id = kyc_res.json()["id"]

    client.post(f"/api/v1/kyc/admin/{kyc_id}/decision", json={"decision": "VERIFIED"}, headers=admin_headers)

    # 4. Create Farm and Parcel
    farm_res = client.post("/api/v1/farms", json={
        "farm_name": "Shinde Agro Estate",
        "state": "Maharashtra",
        "district": "Pune",
        "taluka": "Baramati",
        "village": "Malegaon",
        "pincode": "413115",
        "total_area_acres": 8.0
    }, headers=farmer_headers)
    assert farm_res.status_code == 201
    farm_id = farm_res.json()["id"]

    parcel_res = client.post(f"/api/v1/farms/{farm_id}/parcels", json={
        "survey_number": "205/B",
        "sub_division_no": "1",
        "area_acres": 5.0,
        "center_latitude": 18.15,
        "center_longitude": 74.58,
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[[74.58, 18.15], [74.59, 18.15], [74.59, 18.16], [74.58, 18.16], [74.58, 18.15]]]
        },
        "soil_type": "Black Cotton",
        "irrigation_source": "Drip"
    }, headers=farmer_headers)
    assert parcel_res.status_code == 201
    parcel_id = parcel_res.json()["id"]

    # 5. Create Project
    proj_res = client.post("/api/v1/projects", json={
        "farm_id": farm_id,
        "parcel_id": parcel_id,
        "title": "High-Density Pomegranate Plantation 2026",
        "crop_name": "Pomegranate",
        "crop_variety": "Bhagwa",
        "season": "Kharif",
        "sowing_date": "2026-06-15",
        "estimated_harvest_date": "2026-12-15",
        "total_valuation_inr": 500000.0,
        "farmer_equity_percent": 30.0,
        "total_shares": 100,
        "expected_yield_quintals": 120.0,
        "expected_revenue_inr": 900000.0
    }, headers=farmer_headers)
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    # Advance project state: DRAFT -> SUBMITTED -> UNDER_VERIFICATION -> VERIFIED -> OPEN_FOR_FUNDING
    for state in ["SUBMITTED", "UNDER_VERIFICATION", "VERIFIED", "OPEN_FOR_FUNDING"]:
        trans_res = client.post(f"/api/v1/projects/{project_id}/transition", json={
            "next_state": state,
            "remarks": f"Transitioned to {state}"
        }, headers=admin_headers)
        assert trans_res.status_code == 200

    return {
        "farmer_headers": farmer_headers,
        "admin_headers": admin_headers,
        "project_id": project_id
    }


def test_investor_payment_orders_and_verification(client: TestClient):
    """Verifies Razorpay order creation, payment verification, digital share allocation, and ledger recording."""
    env = create_seeded_farmer_and_project(client)
    project_id = env["project_id"]

    # 1. Register Investor
    inv_reg = client.post("/api/v1/auth/register", json={
        "email": "radha.investor@agristack.org",
        "phone_number": "+919833445566",
        "password": "InvestorPass2026!",
        "full_name": "Radha Sharma",
        "primary_role": "INVESTOR",
        "preferred_language": "en"
    })
    assert inv_reg.status_code == 201
    inv_token = inv_reg.json()["access_token"]
    inv_headers = {"Authorization": f"Bearer {inv_token}"}

    # 2. Investor creates payment order for 10 shares (10 * 5,000 = 50,000 INR)
    order_res = client.post("/api/v1/payments/orders", json={
        "project_id": project_id,
        "num_shares": 10
    }, headers=inv_headers)
    assert order_res.status_code == 201
    order_data = order_res.json()
    assert order_data["amount_inr"] == 50000.0
    assert order_data["razorpay_order_id"].startswith("order_rzp_")
    rzp_order_id = order_data["razorpay_order_id"]

    # 3. Investor verifies signature (mocking successful Razorpay checkout in sandbox)
    verify_res = client.post("/api/v1/payments/verify", json={
        "razorpay_order_id": rzp_order_id,
        "razorpay_payment_id": "pay_rzp_test_12345",
        "razorpay_signature": "test_sig_valid_hash"
    }, headers=inv_headers)
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["success"] is True
    assert verify_data["shares_purchased"] == 10

    # 4. Check Investor Portfolio
    port_res = client.get("/api/v1/payments/my-investments", headers=inv_headers)
    assert port_res.status_code == 200
    investments = port_res.json()
    assert len(investments) == 1
    assert investments[0]["share_count"] == 10
    assert investments[0]["total_amount_inr"] == 50000.0
    assert investments[0]["escrow_status"] == "HELD_IN_ESCROW"


def test_marketplace_produce_listing_sale_and_otp(client: TestClient):
    """Tests farmer B2B listing creation, produce sale submission with APMC anomaly check, and buyer OTP verification."""
    env = create_seeded_farmer_and_project(client)
    project_id = env["project_id"]
    farmer_headers = env["farmer_headers"]
    admin_headers = env["admin_headers"]

    # Fund the project and advance to IN_PROGRESS
    client.post(f"/api/v1/projects/{project_id}/transition", json={
        "next_state": "FUNDED",
        "remarks": "Project fully funded"
    }, headers=admin_headers)

    client.post(f"/api/v1/projects/{project_id}/transition", json={
        "next_state": "IN_PROGRESS",
        "remarks": "Cultivation initiated"
    }, headers=admin_headers)

    # 1. Farmer creates Produce Listing
    listing_res = client.post("/api/v1/marketplace/listings", json={
        "project_id": project_id,
        "crop_name": "Bhagwa Pomegranate",
        "quantity_kg": 5000.0,
        "asking_price_per_kg": 120.0,
        "description": "Export-quality Bhagwa variety, residue-free."
    }, headers=farmer_headers)
    assert listing_res.status_code == 201
    listing = listing_res.json()
    assert listing["crop_name"] == "Bhagwa Pomegranate"
    assert listing["status"] == "ACTIVE"
    listing_id = listing["id"]

    # 2. Browse listings
    browse_res = client.get("/api/v1/marketplace/listings?crop_name=Pomegranate", headers=farmer_headers)
    assert browse_res.status_code == 200
    assert len(browse_res.json()) >= 1

    # 3. Farmer submits Sale with APMC price anomaly check
    # APMC price is 100/kg; sale is 135/kg (>25% deviation -> flags record)
    sale_res = client.post("/api/v1/marketplace/sales", json={
        "listing_id": listing_id,
        "buyer_name": "Reliance Fresh Wholesale Ltd",
        "buyer_contact": "+919800112233",
        "quantity_kg": 2000.0,
        "sale_price_per_kg": 135.0,
        "apmc_reference_price": 100.0,
        "invoice_url": "https://s3.amazonaws.com/agristack/invoices/inv_001.pdf"
    }, headers=farmer_headers)
    assert sale_res.status_code == 201
    sale = sale_res.json()
    assert sale["total_amount"] == 270000.0
    assert sale["is_flagged"] is True  # >25% deviation flagged for audit!
    sale_id = sale["id"]

    # 4. Buyer confirms delivery via OTP (in sandbox, retrieve OTP from service or mock)
    from app.services.marketplace_service import _generate_otp
    # Test incorrect OTP
    bad_otp_res = client.post(f"/api/v1/marketplace/sales/{sale_id}/verify-otp", json={
        "otp": "000000"
    }, headers=farmer_headers)
    assert bad_otp_res.status_code == 400

    # Project sales lookup
    proj_sales_res = client.get(f"/api/v1/marketplace/sales/project/{project_id}", headers=farmer_headers)
    assert proj_sales_res.status_code == 200
    assert len(proj_sales_res.json()) == 1


def test_pro_rata_settlement_and_investor_payout(client: TestClient):
    """Tests harvest completion, pro-rata returns calculation (Gross - Expenses - 5% Platform Fee + Insurance), and investor payouts."""
    env = create_seeded_farmer_and_project(client)
    project_id = env["project_id"]
    admin_headers = env["admin_headers"]

    # Register 2 investors buying shares
    inv1_reg = client.post("/api/v1/auth/register", json={
        "email": "investor1@agristack.org",
        "phone_number": "+919811111111",
        "password": "Password123!",
        "full_name": "Investor One",
        "primary_role": "INVESTOR",
        "preferred_language": "en"
    })
    inv1_headers = {"Authorization": f"Bearer {inv1_reg.json()['access_token']}"}

    inv2_reg = client.post("/api/v1/auth/register", json={
        "email": "investor2@agristack.org",
        "phone_number": "+919822222222",
        "password": "Password123!",
        "full_name": "Investor Two",
        "primary_role": "INVESTOR",
        "preferred_language": "en"
    })
    inv2_headers = {"Authorization": f"Bearer {inv2_reg.json()['access_token']}"}

    # Buy 20 shares and 30 shares
    ord1 = client.post("/api/v1/payments/orders", json={"project_id": project_id, "num_shares": 20}, headers=inv1_headers)
    client.post("/api/v1/payments/verify", json={
        "razorpay_order_id": ord1.json()["razorpay_order_id"],
        "razorpay_payment_id": "pay_inv1",
        "razorpay_signature": "test_sig_1"
    }, headers=inv1_headers)

    ord2 = client.post("/api/v1/payments/orders", json={"project_id": project_id, "num_shares": 30}, headers=inv2_headers)
    client.post("/api/v1/payments/verify", json={
        "razorpay_order_id": ord2.json()["razorpay_order_id"],
        "razorpay_payment_id": "pay_inv2",
        "razorpay_signature": "test_sig_2"
    }, headers=inv2_headers)

    # Advance project lifecycle to HARVESTED -> SOLD
    for state in ["FUNDED", "IN_PROGRESS", "HARVESTED", "SOLD"]:
        client.post(f"/api/v1/projects/{project_id}/transition", json={
            "next_state": state,
            "remarks": f"State advance to {state}"
        }, headers=admin_headers)

    # Admin initiates Settlement:
    # Gross Revenue: 1,000,000 INR
    # Total Expenses: 300,000 INR
    # Platform Fee 5%: 50,000 INR
    # Insurance: 0.0
    # Net Distributable: 1,000,000 - 300,000 - 50,000 = 650,000 INR
    # Investor Pool (70%): 650,000 * 0.70 = 455,000 INR
    # Total Investor Shares = 50. Per-share return = 455,000 / 50 = 9,100 INR per share!
    # Investor 1 (20 shares): 182,000 INR
    # Investor 2 (30 shares): 273,000 INR
    settle_res = client.post("/api/v1/settlements/", json={
        "project_id": project_id,
        "gross_revenue": 1000000.0,
        "total_expenses": 300000.0,
        "insurance_recovered": 0.0,
        "notes": "Pomegranate crop season final audit and dividend disbursement."
    }, headers=admin_headers)
    assert settle_res.status_code == 201
    settle_data = settle_res.json()
    assert settle_data["status"] == "COMPLETED"
    assert settle_data["gross_revenue"] == 1000000.0
    assert settle_data["platform_fee"] == 50000.0
    assert settle_data["net_distributable"] == 650000.0

    # Investor 1 checks payouts
    payout_res = client.get("/api/v1/settlements/my-payouts", headers=inv1_headers)
    assert payout_res.status_code == 200
    payouts = payout_res.json()
    assert len(payouts) == 1
    assert payouts[0]["shares_held"] == 20
    assert abs(payouts[0]["payout_amount"] - 182000.0) < 1.0

    payout_id = payouts[0]["id"]

    # Admin marks payout as transferred via Razorpay Payouts UTR
    transfer_res = client.patch(f"/api/v1/settlements/payouts/{payout_id}/transfer", json={
        "transfer_reference": "UTR_RZP_HDFC_998877665544"
    }, headers=admin_headers)
    assert transfer_res.status_code == 200
    assert transfer_res.json()["status"] == "TRANSFERRED"


def test_crop_failure_and_general_disputes(client: TestClient):
    """Tests crop failure claims with PMFBY insurance linkage, admin review, and general disputes resolution."""
    env = create_seeded_farmer_and_project(client)
    project_id = env["project_id"]
    farmer_headers = env["farmer_headers"]
    admin_headers = env["admin_headers"]

    # Advance project to IN_PROGRESS
    for state in ["FUNDED", "IN_PROGRESS"]:
        client.post(f"/api/v1/projects/{project_id}/transition", json={
            "next_state": state,
            "remarks": f"State advance to {state}"
        }, headers=admin_headers)

    # 1. Farmer submits crop failure claim (e.g. unseasonal hailstorm)
    claim_res = client.post("/api/v1/disputes/crop-failure", json={
        "project_id": project_id,
        "failure_reason": "Severe hailstorm damaged flowering crop",
        "affected_area_pct": 65.0,
        "insurance_policy_number": "PMFBY-MAH-2026-887766",
        "evidence_urls": [
            "https://s3.amazonaws.com/agristack/damage/field1.jpg",
            "https://s3.amazonaws.com/agristack/damage/field2.jpg"
        ]
    }, headers=farmer_headers)
    assert claim_res.status_code == 201
    claim = claim_res.json()
    assert claim["status"] == "PENDING"
    assert claim["affected_area_pct"] == 65.0
    claim_id = claim["id"]

    # 2. Admin views pending claims
    pending_res = client.get("/api/v1/disputes/crop-failure/pending", headers=admin_headers)
    assert pending_res.status_code == 200
    assert len(pending_res.json()) >= 1

    # 3. Admin approves claim and links insurance payout
    review_res = client.patch(f"/api/v1/disputes/crop-failure/{claim_id}/review", json={
        "decision": "APPROVED",
        "insurance_approved_amount": 220000.0,
        "admin_notes": "Surveyor inspected field on 14th Oct. Approved 65% loss compensation under PMFBY."
    }, headers=admin_headers)
    assert review_res.status_code == 200
    assert review_res.json()["status"] == "APPROVED"
    assert review_res.json()["insurance_approved_amount"] == 220000.0

    # 4. User raises general dispute
    disp_res = client.post("/api/v1/disputes/", json={
        "project_id": project_id,
        "dispute_type": "WATER_LOGGING_CONCERN",
        "description": "Neighboring canal overflowed into North parcel",
        "evidence_urls": []
    }, headers=farmer_headers)
    assert disp_res.status_code == 201
    dispute_id = disp_res.json()["id"]

    # 5. Admin lists open disputes & resolves
    open_res = client.get("/api/v1/disputes/open", headers=admin_headers)
    assert open_res.status_code == 200
    assert any(d["id"] == dispute_id for d in open_res.json())

    resolve_res = client.patch(f"/api/v1/disputes/{dispute_id}/resolve", json={
        "resolution": "RESOLVED_LOCAL_PANCHAYAT",
        "resolution_notes": "Canal gate repaired by Gram Panchayat irrigation committee."
    }, headers=admin_headers)
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"
