from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database.session import get_db
from app.core.config import settings
from app.schemas.health import HealthLiveResponse, HealthReadyResponse
import redis.asyncio as aioredis

router = APIRouter(prefix="/health", tags=["Health Checks"])

@router.get("/live", response_model=HealthLiveResponse)
async def health_live():
    """
    Liveness probe: verifies that the FastAPI application process is running.
    Does not expose sensitive infrastructure details.
    """
    return HealthLiveResponse(
        status="ok",
        service=settings.APP_NAME,
        environment=settings.APP_ENV
    )

@router.get("/ready", response_model=HealthReadyResponse)
async def health_ready(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe: verifies connectivity to PostgreSQL database and Redis cache.
    """
    db_status = "unhealthy"
    redis_status = "unhealthy"

    # Probe Database
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    # Probe Redis
    try:
        r = aioredis.from_url(settings.REDIS_URL, socket_timeout=1.0)
        await r.ping()
        await r.aclose()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"

    all_healthy = db_status == "connected" and redis_status == "connected"

    return HealthReadyResponse(
        status="ok" if all_healthy else "degraded",
        service=settings.APP_NAME,
        database=db_status,
        redis=redis_status,
        dependencies_healthy=all_healthy
    )

