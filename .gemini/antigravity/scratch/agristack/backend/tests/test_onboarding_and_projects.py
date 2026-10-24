import pytest
from fastapi.testclient import TestClient

def test_full_farmer_onboarding_project_and_escrow_flow(client: TestClient):
    # --- 1. Farmer Registration & Login ---
    farmer_reg = client.post("/api/v1/auth/register", json={
        "email": "tukaram.farmer@agristack.org",
        "phone_number": "+919822334455",
        "password": "FarmerPassword2026!",
        "full_name": "Tukaram Patil",
        "primary_role": "FARMER",
        "preferred_language": "mr"
    })
    assert farmer_reg.status_code == 201
    farmer_token = farmer_reg.json()["access_token"]
    farmer_headers = {"Authorization": f"Bearer {farmer_token}"}

    # --- 2. Admin Login ---
    admin_login = client.post("/api/v1/auth/login", json={
        "email_or_phone": "admin@agristack.org",
        "password": "AgriStack@Admin2026"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # --- 3. Step 1 & 2: Farmer KYC Submission & Aadhaar Masking ---
    kyc_res = client.post("/api/v1/kyc/submit", json={
        "aadhaar_number": "987654321099",
        "pan_number": "ABCDE1234F",
        "satbara_document_url": "https://s3.amazonaws.com/agristack-docs/satbara_tukaram.pdf",
        "survey_number_claimed": "142/A"
    }, headers=farmer_headers)
    assert kyc_res.status_code == 200
    kyc_data = kyc_res.json()
    assert kyc_data["aadhaar_last4"] == "1099"  # Privacy check: only last 4 digits returned
    assert kyc_data["verification_status"] == "SUBMITTED"
    kyc_id = kyc_data["id"]

    # --- 4. Admin Approves Farmer KYC ---
    decision_res = client.post(f"/api/v1/kyc/admin/{kyc_id}/decision", json={
        "decision": "VERIFIED"
    }, headers=admin_headers)
    assert decision_res.status_code == 200
    assert decision_res.json()["verification_status"] == "VERIFIED"

    # --- 5. Farm & Land Parcel Registration ---
    farm_res = client.post("/api/v1/farms", json={
        "farm_name": "Godavari Valley Agro",
        "state": "Maharashtra",
        "district": "Nashik",
        "taluka": "Niphad",
        "village": "Pimpalgaon",
        "pincode": "422209",
        "total_area_acres": 10.5
    }, headers=farmer_headers)
    assert farm_res.status_code == 201
    farm_id = farm_res.json()["id"]

    # Add Parcel with GeoJSON polygon
    parcel_res = client.post(f"/api/v1/farms/{farm_id}/parcels", json={
        "survey_number": "142/A",
        "sub_division_no": "1",
        "area_acres": 5.0,
        "center_latitude": 20.088,
        "center_longitude": 73.985,
        "boundary_geojson": {
            "type": "Polygon",
            "coordinates": [[[73.98, 20.08], [73.99, 20.08], [73.99, 20.09], [73.98, 20.09], [73.98, 20.08]]]
        },
        "soil_type": "Black Cotton",
        "irrigation_source": "Drip"
    }, headers=farmer_headers)
    assert parcel_res.status_code == 201
    parcel_data = parcel_res.json()
    parcel_id = parcel_data["id"]
    assert parcel_data["is_verified"] is True  # 7/12 Satbara match confirmed!
    assert parcel_data["duplicate_flag"] is False

    # --- 6. Project Creation (Soybean Kharif) ---
    proj_res = client.post("/api/v1/projects", json={
        "farm_id": farm_id,
        "parcel_id": parcel_id,
        "title": "Kharif 2026 Certified Soybean Enterprise",
        "crop_name": "Soybean",
        "crop_variety": "JS 335",
        "season": "Kharif",
        "sowing_date": "2026-06-15",
        "estimated_harvest_date": "2026-10-25",
        "total_valuation_inr": 200000.0,
        "farmer_equity_percent": 30.0,
        "total_shares": 100,
        "expected_yield_quintals": 45.0,
        "expected_revenue_inr": 315000.0
    }, headers=farmer_headers)
    assert proj_res.status_code == 201
    proj_data = proj_res.json()
    project_id = proj_data["id"]
    assert proj_data["status"] == "DRAFT"
    assert proj_data["share_price_inr"] == 2000.0
    assert proj_data["investor_pool_percent"] == 70.0

    # --- 7. Verify Milestone Escrow Generation (40 / 40 / 20) ---
    milestones_res = client.get(f"/api/v1/projects/{project_id}/milestones", headers=farmer_headers)
    assert milestones_res.status_code == 200
    milestones = milestones_res.json()
    assert len(milestones) == 3
    assert milestones[0]["percentage_release"] == 40.0
    assert milestones[1]["percentage_release"] == 40.0
    assert milestones[2]["percentage_release"] == 20.0
    # Target investor pool is 70% of 200,000 = 140,000.
    # Milestone 1 (40%) = 56,000 INR
    assert milestones[0]["amount_inr"] == 56000.0

    # --- 8. Verify Farmer Genesis Digital Shares & Cryptographic Ledger ---
    shares_res = client.get(f"/api/v1/projects/{project_id}/shares", headers=farmer_headers)
    assert shares_res.status_code == 200
    shares = shares_res.json()
    assert len(shares) == 1
    assert shares[0]["share_count"] == 30
    assert shares[0]["holding_type"] == "FARMER_EQUITY"

    ledger_res = client.get(f"/api/v1/ledger/project/{project_id}", headers=farmer_headers)
    assert ledger_res.status_code == 200
    ledger_entries = ledger_res.json()
    assert len(ledger_entries) == 1
    assert ledger_entries[0]["transaction_type"] == "GENESIS_ISSUANCE"

    integrity_res = client.get(f"/api/v1/ledger/verify-integrity/{project_id}", headers=farmer_headers)
    assert integrity_res.status_code == 200
    assert integrity_res.json()["is_valid"] is True

    # --- 9. State Machine Transitions & RBAC ---
    # Farmer submits draft project
    submit_res = client.post(f"/api/v1/projects/{project_id}/transition", json={
        "next_state": "SUBMITTED",
        "rationale": "Farmer finalized budget and documents"
    }, headers=farmer_headers)
    assert submit_res.status_code == 200
    assert submit_res.json()["status"] == "SUBMITTED"

    # Farmer cannot self-verify (only Admin can)
    illegal_verify = client.post(f"/api/v1/projects/{project_id}/transition", json={
        "next_state": "VERIFIED"
    }, headers=farmer_headers)
    assert illegal_verify.status_code == 422  # Must go through UNDER_VERIFICATION first

    # Admin moves through verification pipeline
    client.post(f"/api/v1/projects/{project_id}/transition", json={
        "next_state": "UNDER_VERIFICATION"
    }, headers=admin_headers)
    client.post(f"/api/v1/projects/{project_id}/transition", json={
        "next_state": "VERIFIED"
    }, headers=admin_headers)
    open_res = client.post(f"/api/v1/projects/{project_id}/transition", json={
        "next_state": "OPEN_FOR_FUNDING"
    }, headers=admin_headers)
    assert open_res.status_code == 200
    assert open_res.json()["status"] == "OPEN_FOR_FUNDING"

    # Transition to FUNDED
    client.post(f"/api/v1/projects/{project_id}/transition", json={
        "next_state": "FUNDED"
    }, headers=admin_headers)

    # --- 10. Milestone 1 Sowing Proof Upload & Escrow Release ---
    # Farmer uploads sowing proof
    proof_res = client.post(
        f"/api/v1/projects/{project_id}/milestones/1/proof?proof_url=https://s3.amazonaws.com/agristack/sowing_photo.jpg&notes=Seed_batch_JS335_sown",
        headers=farmer_headers
    )
    assert proof_res.status_code == 200

    # Admin releases Milestone 1 funds
    milestone_1_id = milestones[0]["id"]
    release_res = client.post(
        f"/api/v1/projects/milestones/{milestone_1_id}/release?notes=Sowing_verified_via_photo",
        headers=admin_headers
    )
    assert release_res.status_code == 200

    # Project should now be IN_PROGRESS!
    updated_proj = client.get(f"/api/v1/projects/{project_id}", headers=farmer_headers).json()
    assert updated_proj["status"] == "IN_PROGRESS"

    # Ledger must now contain 2 entries (GENESIS_ISSUANCE + ESCROW_PAYOUT) and be 100% cryptographically intact!
    final_integrity = client.get(f"/api/v1/ledger/verify-integrity/{project_id}", headers=admin_headers).json()
    assert final_integrity["is_valid"] is True
    assert final_integrity["entries_audited"] == 2
