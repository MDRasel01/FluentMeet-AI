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

import app.models  # Ensure all tables including audio models are registered
from app.models.base import Base
from app.database.session import get_db
import app.database.session as app_session_mod
from app.services.email_service import email_service
from sqlalchemy.pool import StaticPool
from app.main import app

test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
app_session_mod.AsyncSessionLocal = TestSessionLocal

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Clear sent emails
    if hasattr(email_service.provider, "sent_emails"):
        email_service.provider.sent_emails.clear()
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
    payload = {
        "email": "testuser@fluentmeet.ai",
        "password": "Password123!",
        "full_name": "Test User",
        "native_language": "Spanish",
        "terms_accepted": True,
        "privacy_accepted": True,
    }
    reg_resp = await async_client.post("/api/v1/auth/register", json=payload)
    user_id = reg_resp.json()["data"]["id"]

    login_resp = await async_client.post("/api/v1/auth/login", json={
        "email": "testuser@fluentmeet.ai",
        "password": "Password123!"
    })
    data = login_resp.json()["data"]
    token = data["access_token"]
    refresh_token = data["refresh_token"]
    return {
        "user_id": user_id,
        "email": "testuser@fluentmeet.ai",
        "token": token,
        "refresh_token": refresh_token,
        "headers": {"Authorization": f"Bearer {token}"}
    }

@pytest_asyncio.fixture
async def second_user_token(async_client: AsyncClient) -> dict:
    payload = {
        "email": "user2@fluentmeet.ai",
        "password": "Password123!",
        "full_name": "Second User",
        "native_language": "German",
        "terms_accepted": True,
        "privacy_accepted": True,
    }
    reg_resp = await async_client.post("/api/v1/auth/register", json=payload)
    user_id = reg_resp.json()["data"]["id"]

    login_resp = await async_client.post("/api/v1/auth/login", json={
        "email": "user2@fluentmeet.ai",
        "password": "Password123!"
    })
    data = login_resp.json()["data"]
    token = data["access_token"]
    refresh_token = data["refresh_token"]
    return {
        "user_id": user_id,
        "email": "user2@fluentmeet.ai",
        "token": token,
        "refresh_token": refresh_token,
        "headers": {"Authorization": f"Bearer {token}"}
    }
