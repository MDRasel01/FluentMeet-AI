"""
FluentMeet AI - Step 08 Negative & Resilience Tests: Analysis Engine
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_trigger_analysis_nonexistent_meeting(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]
    resp = await async_client.post(
        "/api/v1/meetings/00000000-0000-0000-0000-000000000000/analysis",
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_status_nonexistent_session(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]
    resp = await async_client.get(
        "/api/v1/analysis/00000000-0000-0000-0000-000000000000/status",
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_participant_details_nonexistent(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]
    resp = await async_client.get(
        "/api/v1/analysis/00000000-0000-0000-0000-000000000000/participants/00000000-0000-0000-0000-000000000001",
        headers=headers,
    )
    assert resp.status_code == 404
