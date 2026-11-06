import re
import pytest
from httpx import AsyncClient
from app.services.email_service import email_service

@pytest.mark.asyncio
async def test_organization_lifecycle(
    async_client: AsyncClient,
    auth_token: dict,
    second_user_token: dict
):
    owner_headers = auth_token["headers"]
    member_headers = second_user_token["headers"]
    member_email = second_user_token["email"]

    # 1. Create Organization
    create_resp = await async_client.post(
        "/api/v1/organizations",
        json={"name": "Acme Global Engineering", "slug": "acme-global"},
        headers=owner_headers
    )
    assert create_resp.status_code == 201
    org_data = create_resp.json()["data"]
    org_id = org_data["id"]
    assert org_data["name"] == "Acme Global Engineering"
    assert org_data["my_role"] == "owner"

    # 2. List organizations
    list_resp = await async_client.get("/api/v1/organizations", headers=owner_headers)
    assert list_resp.status_code == 200
    orgs = list_resp.json()["data"]
    assert any(o["id"] == org_id for o in orgs)

    # 3. Invite second user as Manager
    inv_resp = await async_client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"invited_email": member_email, "role": "manager"},
        headers=owner_headers
    )
    assert inv_resp.status_code == 201
    assert inv_resp.json()["data"]["invited_email"] == member_email

    # Extract invitation token from sent email
    last_email = email_service.provider.sent_emails[-1]
    match = re.search(r"token=([A-Za-z0-9_\-]+)", last_email["text"])
    assert match is not None
    inv_token = match.group(1)

    # 4. Second user accepts invitation
    accept_resp = await async_client.post(
        "/api/v1/invitations/accept",
        json={"token": inv_token},
        headers=member_headers
    )
    assert accept_resp.status_code == 200
    assert accept_resp.json()["data"]["role"] == "manager"

    # 5. List members shows both Owner and Manager
    members_resp = await async_client.get(f"/api/v1/organizations/{org_id}/members", headers=owner_headers)
    assert members_resp.status_code == 200
    members = members_resp.json()["data"]
    assert len(members) == 2

    # 6. Privilege escalation check: Manager tries to invite someone as Owner -> MUST FAIL
    esc_resp = await async_client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"invited_email": "someone@fluentmeet.ai", "role": "owner"},
        headers=member_headers
    )
    assert esc_resp.status_code == 403

    # 7. Role management: Owner updates second user role to Admin
    target_user_id = second_user_token["user_id"]
    update_role_resp = await async_client.patch(
        f"/api/v1/organizations/{org_id}/members/{target_user_id}",
        json={"role": "admin"},
        headers=owner_headers
    )
    assert update_role_resp.status_code == 200
    assert update_role_resp.json()["data"]["role"] == "admin"

    # 8. Ownership transfer: Owner transfers to new Admin
    transfer_resp = await async_client.post(
        f"/api/v1/organizations/{org_id}/transfer-ownership",
        json={"new_owner_user_id": target_user_id, "password": "Password123!"},
        headers=owner_headers
    )
    assert transfer_resp.status_code == 200

    # Verify new owner role
    new_owner_org = await async_client.get(f"/api/v1/organizations/{org_id}", headers=member_headers)
    assert new_owner_org.status_code == 200
    assert new_owner_org.json()["data"]["my_role"] == "owner"

