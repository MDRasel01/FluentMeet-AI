import re
import pytest
from httpx import AsyncClient
from app.services.email_service import email_service

@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    payload = {
        "email": "newuser@fluentmeet.ai",
        "password": "Password123!",
        "confirm_password": "Password123!",
        "full_name": "New User",
        "native_language": "Japanese",
        "terms_accepted": True,
        "privacy_accepted": True,
    }
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["email"] == "newuser@fluentmeet.ai"
    assert body["data"]["status"] == "pending_verification"
    assert body["data"]["is_verified"] is False

    # Check that verification email was dispatched
    assert len(email_service.provider.sent_emails) >= 1
    last_email = email_service.provider.sent_emails[-1]
    assert last_email["to"] == "newuser@fluentmeet.ai"
    assert "token=" in last_email["text"]

@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient):
    payload = {
        "email": "dupe@fluentmeet.ai",
        "password": "Password123!",
        "full_name": "Dupe User",
    }
    resp1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 409
    body = resp2.json()
    assert body["success"] is False

@pytest.mark.asyncio
async def test_email_verification_flow(async_client: AsyncClient):
    # 1. Register
    payload = {
        "email": "verify_me@fluentmeet.ai",
        "password": "Password123!",
        "full_name": "Verify User",
    }
    await async_client.post("/api/v1/auth/register", json=payload)

    # 2. Extract verification token from mock email
    last_email = email_service.provider.sent_emails[-1]
    match = re.search(r"token=([A-Za-z0-9_\-]+)", last_email["text"])
    assert match is not None
    token = match.group(1)

    # 3. Call verify email endpoint
    verify_resp = await async_client.post("/api/v1/auth/verify-email", json={"token": token})
    assert verify_resp.status_code == 200
    assert verify_resp.json()["data"] is True

    # 4. Calling verify again with the same single-use token fails
    re_verify_resp = await async_client.post("/api/v1/auth/verify-email", json={"token": token})
    assert re_verify_resp.status_code == 400

@pytest.mark.asyncio
async def test_login_and_logout(async_client: AsyncClient):
    # 1. Register
    payload = {
        "email": "loginuser@fluentmeet.ai",
        "password": "Password123!",
        "full_name": "Login User",
    }
    await async_client.post("/api/v1/auth/register", json=payload)

    # 2. Login
    login_resp = await async_client.post("/api/v1/auth/login", json={
        "email": "loginuser@fluentmeet.ai",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200
    data = login_resp.json()["data"]
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    assert access_token is not None
    assert refresh_token is not None

    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. List active sessions
    sess_resp = await async_client.get("/api/v1/auth/sessions", headers=headers)
    assert sess_resp.status_code == 200
    sessions = sess_resp.json()["data"]
    assert len(sessions) >= 1

    # 4. Logout
    logout_resp = await async_client.post("/api/v1/auth/logout", headers=headers)
    assert logout_resp.status_code == 200

@pytest.mark.asyncio
async def test_refresh_token_rotation_and_reuse_detection(async_client: AsyncClient):
    # 1. Register & Login
    payload = {
        "email": "refresh_user@fluentmeet.ai",
        "password": "Password123!",
        "full_name": "Refresh User",
    }
    await async_client.post("/api/v1/auth/register", json=payload)

    login_resp = await async_client.post("/api/v1/auth/login", json={
        "email": "refresh_user@fluentmeet.ai",
        "password": "Password123!"
    })
    initial_refresh = login_resp.json()["data"]["refresh_token"]

    # 2. Valid refresh rotation
    ref1_resp = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": initial_refresh})
    assert ref1_resp.status_code == 200
    new_refresh = ref1_resp.json()["data"]["refresh_token"]
    assert new_refresh != initial_refresh

    # 3. REUSE DETECTION: Presenting the old (already used) initial_refresh token must fail with 401
    reuse_resp = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": initial_refresh})
    assert reuse_resp.status_code == 401
    assert "reuse detected" in reuse_resp.json()["message"].lower()

    # 4. Because reuse was detected, the entire family is revoked, so even the new_refresh is invalidated!
    ref2_resp = await async_client.post("/api/v1/auth/refresh", json={"refresh_token": new_refresh})
    assert ref2_resp.status_code == 401

@pytest.mark.asyncio
async def test_password_reset_flow(async_client: AsyncClient):
    # 1. Register
    email = "forgot_user@fluentmeet.ai"
    await async_client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "OldPassword123!",
        "full_name": "Forgot User",
    })

    # 2. Request reset
    req_resp = await async_client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert req_resp.status_code == 200

    # 3. Extract reset token
    last_email = email_service.provider.sent_emails[-1]
    match = re.search(r"token=([A-Za-z0-9_\-]+)", last_email["text"])
    assert match is not None
    token = match.group(1)

    # 4. Perform reset
    reset_resp = await async_client.post("/api/v1/auth/reset-password", json={
        "token": token,
        "new_password": "NewBrandPassword123!",
        "confirm_password": "NewBrandPassword123!"
    })
    assert reset_resp.status_code == 200

    # 5. Old password fails
    fail_login = await async_client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "OldPassword123!"
    })
    assert fail_login.status_code == 401

    # 6. New password succeeds
    good_login = await async_client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "NewBrandPassword123!"
    })
    assert good_login.status_code == 200
