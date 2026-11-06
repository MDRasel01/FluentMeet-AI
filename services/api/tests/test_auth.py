import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    payload = {
        "email": "newuser@fluentmeet.ai",
        "password": "Password123!",
        "full_name": "New User",
        "native_language": "Japanese"
    }
    resp = await async_client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["email"] == "newuser@fluentmeet.ai"
    assert body["data"]["full_name"] == "New User"

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
    assert resp2.status_code == 400
    body = resp2.json()
    assert body["success"] is False

@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    payload = {
        "email": "loginuser@fluentmeet.ai",
        "password": "Password123!",
        "full_name": "Login User",
    }
    await async_client.post("/api/v1/auth/register", json=payload)

    login_resp = await async_client.post("/api/v1/auth/login", json={
        "email": "loginuser@fluentmeet.ai",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200
    body = login_resp.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]

@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient):
    resp = await async_client.post("/api/v1/auth/login", json={
        "email": "nonexistent@fluentmeet.ai",
        "password": "WrongPassword!"
    })
    assert resp.status_code == 401
    body = resp.json()
    assert body["success"] is False
