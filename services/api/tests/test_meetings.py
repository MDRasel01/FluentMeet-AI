import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_list_meetings(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]

    # 1. Create meeting
    payload = {
        "title": "Quarterly Product Planning",
        "platform": "google_meet",
        "meeting_url": "https://meet.google.com/abc-defg-hij",
        "consent_confirmed": True,
        "participants": [
            {"name": "Sarah Connor", "is_local_user": False}
        ]
    }
    create_resp = await async_client.post("/api/v1/meetings", json=payload, headers=headers)
    assert create_resp.status_code == 201
    meeting_data = create_resp.json()["data"]
    meeting_id = meeting_data["id"]
    assert meeting_data["title"] == "Quarterly Product Planning"
    assert meeting_data["status"] == "active"

    # 2. Get meeting by ID
    get_resp = await async_client.get(f"/api/v1/meetings/{meeting_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["id"] == meeting_id

    # 3. List meetings
    list_resp = await async_client.get("/api/v1/meetings", headers=headers)
    assert list_resp.status_code == 200
    meetings = list_resp.json()["data"]
    assert len(meetings) >= 1
    assert any(m["id"] == meeting_id for m in meetings)

    # 4. End meeting
    end_resp = await async_client.patch(f"/api/v1/meetings/{meeting_id}/end", headers=headers)
    assert end_resp.status_code == 200
    assert end_resp.json()["data"]["status"] == "completed"

