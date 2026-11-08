from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.request_id import RequestIdMiddleware
from app.database.session import init_db
from app.schemas.common import ApiResponse

# Routers
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.meetings import router as meetings_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.invitations import router as invitations_router
from app.api.v1.permissions import router as permissions_router
from app.api.v1.audio import router as audio_router
from app.api.v1.transcripts import router as transcripts_router
from app.api.v1.extensions import router as extensions_router
from app.api.v1.admin_extensions import router as admin_extensions_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.pronunciation import router as pronunciation_router
from app.websocket.endpoint import router as ws_router

# Setup structured logger
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FluentMeet AI API service...")
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.warning(f"Database initialization warning (may use external migrations in prod): {e}")
    yield
    logger.info("Shutting down FluentMeet AI API service...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="FluentMeet AI Core Backend REST & WebSocket Services",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Custom Middlewares
app.add_middleware(RequestIdMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse.error_response(message=str(exc.detail)).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = errors[0].get("msg") if errors else "Validation error"
    field = ".".join(str(loc) for loc in errors[0].get("loc", [])) if errors else ""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ApiResponse.error_response(message=f"Validation failed at '{field}': {msg}").model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse.error_response(message="Internal server error").model_dump()
    )

# Include API Routers
app.include_router(health_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(meetings_router, prefix="/api/v1")
app.include_router(organizations_router, prefix="/api/v1")
app.include_router(invitations_router, prefix="/api/v1")
app.include_router(permissions_router, prefix="/api/v1")
app.include_router(audio_router, prefix="/api/v1")
app.include_router(transcripts_router, prefix="/api/v1")
app.include_router(extensions_router, prefix="/api/v1")
app.include_router(admin_extensions_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(pronunciation_router, prefix="/api/v1")
app.include_router(ws_router)
