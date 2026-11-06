import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_live(async_client: AsyncClient):
    response = await async_client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "FluentMeet AI"
    assert "environment" in data

@pytest.mark.asyncio
async def test_health_ready(async_client: AsyncClient):
    response = await async_client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert "database" in data
    assert "redis" in data
