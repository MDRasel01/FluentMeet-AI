import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_cross_tenant_isolation(
    async_client: AsyncClient,
    auth_token: dict,
    second_user_token: dict
):
    user1_headers = auth_token["headers"]
    user2_headers = second_user_token["headers"]

    # 1. User 1 creates Organization Alpha
    alpha_resp = await async_client.post(
        "/api/v1/organizations",
        json={"name": "Alpha Corp", "slug": "alpha-corp"},
        headers=user1_headers
    )
    assert alpha_resp.status_code == 201
    alpha_id = alpha_resp.json()["data"]["id"]

    # 2. User 2 creates Organization Beta
    beta_resp = await async_client.post(
        "/api/v1/organizations",
        json={"name": "Beta Enterprises", "slug": "beta-ent"},
        headers=user2_headers
    )
    assert beta_resp.status_code == 201
    beta_id = beta_resp.json()["data"]["id"]

    # 3. Cross-Tenant Check: User 2 tries to access Alpha Org details -> MUST BE FORBIDDEN (403)
    unauth_details = await async_client.get(f"/api/v1/organizations/{alpha_id}", headers=user2_headers)
    assert unauth_details.status_code == 403

    # 4. Cross-Tenant Check: User 2 tries to list Alpha members -> MUST BE FORBIDDEN (403)
    unauth_members = await async_client.get(f"/api/v1/organizations/{alpha_id}/members", headers=user2_headers)
    assert unauth_members.status_code == 403

    # 5. Cross-Tenant Check: User 2 tries to invite into Alpha -> MUST BE FORBIDDEN (403)
    unauth_invite = await async_client.post(
        f"/api/v1/organizations/{alpha_id}/invitations",
        json={"invited_email": "attacker@evil.com", "role": "admin"},
        headers=user2_headers
    )
    assert unauth_invite.status_code == 403

    # 6. Cross-Tenant Check: User 2 tries to delete Alpha -> MUST BE FORBIDDEN (403)
    unauth_delete = await async_client.delete(f"/api/v1/organizations/{alpha_id}", headers=user2_headers)
    assert unauth_delete.status_code == 403

    # 7. Verify Alpha is still completely intact and owned by User 1
    alpha_valid = await async_client.get(f"/api/v1/organizations/{alpha_id}", headers=user1_headers)
    assert alpha_valid.status_code == 200
    assert alpha_valid.json()["data"]["name"] == "Alpha Corp"
