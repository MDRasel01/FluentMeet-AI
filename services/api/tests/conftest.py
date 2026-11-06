import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Use in-memory SQLite for tests
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ENVIRONMENT"] = "testing"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-purpose-only-32bytes"

from app.main import app
from app.models.base import Base
from app.database.session import get_db

test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def auth_token(async_client: AsyncClient) -> dict:
    # Register test user
    payload = {
        "email": "testuser@fluentmeet.ai",
        "password": "Password123!",
        "full_name": "Test User",
        "native_language": "Spanish"
    }
    await async_client.post("/api/v1/auth/register", json=payload)
    login_resp = await async_client.post("/api/v1/auth/login", json={
        "email": "testuser@fluentmeet.ai",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    return {
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }
