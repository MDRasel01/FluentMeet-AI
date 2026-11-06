import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_and_update_my_profile(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]

    # 1. Get profile
    get_resp = await async_client.get("/api/v1/users/me", headers=headers)
    assert get_resp.status_code == 200
    user = get_resp.json()["data"]
    assert user["email"] == "testuser@fluentmeet.ai"
    assert user["full_name"] == "Test User"
    assert user["native_language"] == "Spanish"

    # 2. Update profile with PATCH
    patch_resp = await async_client.patch(
        "/api/v1/users/me",
        json={
            "full_name": "Updated Test User",
            "native_language": "French",
            "bio": "Senior Engineer improving English fluency",
            "job_title": "Solutions Architect"
        },
        headers=headers
    )
    assert patch_resp.status_code == 200
    updated_user = patch_resp.json()["data"]
    assert updated_user["full_name"] == "Updated Test User"
    assert updated_user["native_language"] == "French"
    assert updated_user["bio"] == "Senior Engineer improving English fluency"
    assert updated_user["job_title"] == "Solutions Architect"

@pytest.mark.asyncio
async def test_account_deactivation(async_client: AsyncClient):
    # Register single user
    email = "deact_user@fluentmeet.ai"
    password = "Password123!"
    await async_client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Deact User"
    })
    login_resp = await async_client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Deactivate
    deact_resp = await async_client.request(
        "DELETE",
        "/api/v1/users/me",
        json={"password": password, "reason": "Testing deactivation"},
        headers=headers
    )
    assert deact_resp.status_code == 200

    # Logging in with deactivated account fails with 403
    fail_login = await async_client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    assert fail_login.status_code == 403
