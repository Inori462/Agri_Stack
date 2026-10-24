import pytest
from fastapi.testclient import TestClient

def test_register_and_login_flow(client: TestClient):
    # 1. Register new farmer
    reg_payload = {
        "email": "ramesh.patil@example.com",
        "phone_number": "+919876543210",
        "password": "SecurePassword123!",
        "full_name": "Ramesh Patil",
        "primary_role": "FARMER",
        "preferred_language": "mr"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert data["access_token"] != ""
    assert data["primary_role"] == "FARMER"
    assert data["full_name"] == "Ramesh Patil"

    # 2. Duplicate registration should fail
    dup_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 409
    assert dup_res.json()["error"]["code"] == "DUPLICATE_RESOURCE"

    # 3. Successful login
    login_res = client.post("/api/v1/auth/login", json={
        "email_or_phone": "ramesh.patil@example.com",
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["access_token"] != ""
    token = login_data["access_token"]

    # 4. Verify /users/me with Bearer token
    me_res = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "ramesh.patil@example.com"
    assert me_res.json()["preferred_language"] == "mr"

def test_refresh_token_rotation(client: TestClient):
    # Register
    client.post("/api/v1/auth/register", json={
        "email": "investor.mehta@example.com",
        "phone_number": "+919811122233",
        "password": "StrongPassword456!",
        "full_name": "Kavita Mehta",
        "primary_role": "INVESTOR",
        "preferred_language": "en"
    })

    # Login to get refresh token
    login_res = client.post("/api/v1/auth/login", json={
        "email_or_phone": "investor.mehta@example.com",
        "password": "StrongPassword456!"
    })
    refresh_token = login_res.json()["refresh_token"]

    # Refresh token
    refresh_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert new_data["access_token"] != ""
    assert new_data["refresh_token"] != refresh_token  # Must be rotated!

    # Reusing the old refresh token must be rejected
    reuse_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert reuse_res.status_code == 401
