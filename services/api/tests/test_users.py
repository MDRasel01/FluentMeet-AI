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

    # 2. Update profile
    put_resp = await async_client.put(
        "/api/v1/users/me",
        json={"full_name": "Updated Test User", "native_language": "French"},
        headers=headers
    )
    assert put_resp.status_code == 200
    updated_user = put_resp.json()["data"]
    assert updated_user["full_name"] == "Updated Test User"
    assert updated_user["native_language"] == "French"

