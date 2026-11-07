import re
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.database.session import get_db
from app.repositories.extension_release_repository import ExtensionReleaseRepository
from app.services.extension_storage_service import extension_storage
from app.schemas.common import ApiResponse
from app.schemas.extension_release import (
    ExtensionReleaseResponse,
    ExtensionReleaseListResponse
)
from app.api.deps import get_client_ip, get_client_user_agent, security
from app.core.jwt import decode_access_token

router = APIRouter(prefix="/extensions", tags=["Extensions"])

def detect_platform_from_ua(user_agent: str) -> str:
    ua = user_agent.lower()
    if "windows" in ua or "win32" in ua:
        return "Windows"
    elif "macintosh" in ua or "mac os" in ua:
        return "macOS"
    elif "cros" in ua:
        return "ChromeOS"
    elif "linux" in ua:
        return "Linux"
    elif "android" in ua:
        return "Android"
    elif "iphone" in ua or "ipad" in ua:
        return "iOS"
    return "Unknown"

async def get_optional_user_info(request: Request, db: AsyncSession):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # Check query param token if provided
        token = request.query_params.get("token")
        if not token:
            return None, None
    else:
        token = auth_header.split(" ")[1]

    payload = decode_access_token(token)
    if payload:
        return payload.get("sub"), payload.get("org_id")
    return None, None

def format_release_response(release, base_url: str) -> ExtensionReleaseResponse:
    download_url = f"{base_url.rstrip('/')}/api/v1/extensions/releases/{release.id}/download"
    return ExtensionReleaseResponse(
        id=release.id,
        extension_name=release.extension_name,
        version=release.version,
        channel=release.channel,
        status=release.status,
        manifest_version=release.manifest_version,
        build_number=release.build_number,
        git_commit_sha=release.git_commit_sha,
        release_notes=release.release_notes,
        minimum_chrome_version=release.minimum_chrome_version,
        artifact_filename=release.artifact_filename,
        artifact_size_bytes=release.artifact_size_bytes,
        sha256_checksum=release.sha256_checksum,
        download_count=release.download_count,
        download_url=download_url,
        published_at=release.published_at,
        created_at=release.created_at,
        updated_at=release.updated_at,
    )


@router.get("/releases/latest", response_model=ApiResponse[ExtensionReleaseResponse])
async def get_latest_release(
    request: Request,
    channel: str = Query("stable", description="Release channel: stable, beta, internal"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the latest published release for the requested channel.
    Values are resolved directly from database release records and verified storage metadata.
    """
    repo = ExtensionReleaseRepository(db)
    release = await repo.get_latest_published(channel=channel.lower())
    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No published release found for channel '{channel}'."
        )

    base_url = str(request.base_url)
    return ApiResponse.ok_response(
        data=format_release_response(release, base_url),
        message=f"Latest {channel} release retrieved successfully."
    )


@router.get("/releases", response_model=ApiResponse[ExtensionReleaseListResponse])
async def get_version_history(
    request: Request,
    channel: Optional[str] = Query(None, description="Filter by channel"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get version history of published releases for display in Dashboard Version History table.
    """
    repo = ExtensionReleaseRepository(db)
    releases, total = await repo.list_releases(
        channel=channel.lower() if channel else None,
        published_only=True,
        skip=skip,
        limit=limit
    )

    base_url = str(request.base_url)
    items = [format_release_response(r, base_url) for r in releases]

    latest_stable = await repo.get_latest_published("stable")
    current_stable = format_release_response(latest_stable, base_url) if latest_stable else None

    return ApiResponse.ok_response(
        data=ExtensionReleaseListResponse(
            items=items,
            total=total,
            current_stable=current_stable
        ),
        message="Version history retrieved successfully."
    )


@router.get("/releases/latest/download")
async def download_latest_release(
    request: Request,
    channel: str = Query("stable", description="Release channel"),
    token: Optional[str] = Query(None, description="Optional signed download token or auth token"),
    db: AsyncSession = Depends(get_db)
):
    """
    Resolves the latest published release for the specified channel server-side
    and streams the verified ZIP artifact.
    """
    repo = ExtensionReleaseRepository(db)
    release = await repo.get_latest_published(channel=channel.lower())
    if not release or not release.artifact_storage_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No downloadable artifact found for latest release in channel '{channel}'."
        )

    return await _serve_release_download(release, request, db)


@router.get("/releases/{release_id}")
async def get_release_details(
    release_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Get metadata for a specific release.
    """
    repo = ExtensionReleaseRepository(db)
    release = await repo.get_by_id(release_id)
    if not release or release.status != "published":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release not found or not published."
        )

    base_url = str(request.base_url)
    return ApiResponse.ok_response(
        data=format_release_response(release, base_url),
        message="Release details retrieved successfully."
    )


@router.get("/releases/{release_id}/download")
async def download_release(
    release_id: str,
    request: Request,
    token: Optional[str] = Query(None, description="Optional signed download token"),
    db: AsyncSession = Depends(get_db)
):
    """
    Download a specific release ZIP artifact.
    Enforces rules:
    - Only published releases downloadable.
    - Draft, failed, quarantined, or withdrawn releases blocked.
    - Records download log in database.
    - Increments download counter.
    """
    repo = ExtensionReleaseRepository(db)
    release = await repo.get_by_id(release_id)
    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release artifact not found."
        )

    if release.status != "published":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot download release with status '{release.status}'. Only published releases may be downloaded."
        )

    if not release.artifact_storage_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact storage key is not registered for this release."
        )

    return await _serve_release_download(release, request, db)


async def _serve_release_download(release, request: Request, db: AsyncSession):
    repo = ExtensionReleaseRepository(db)
    user_id, org_id = await get_optional_user_info(request, db)
    user_agent = get_client_user_agent(request)
    client_platform = detect_platform_from_ua(user_agent)
    ip_address = get_client_ip(request)
    request_id = getattr(request.state, "request_id", None)

    try:
        artifact_bytes = extension_storage.get_release_artifact(release.artifact_storage_key)
    except FileNotFoundError:
        await repo.record_download_log(
            release_id=release.id,
            user_id=user_id,
            organization_id=org_id,
            download_status="failed",
            client_platform=client_platform,
            request_id=request_id,
            ip_address=ip_address
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact file missing from storage."
        )

    # Verify checksum on retrieval
    calculated_sha = extension_storage.compute_sha256(artifact_bytes)
    if release.sha256_checksum and calculated_sha.lower() != release.sha256_checksum.lower():
        await repo.record_download_log(
            release_id=release.id,
            user_id=user_id,
            organization_id=org_id,
            download_status="blocked",
            client_platform=client_platform,
            request_id=request_id,
            ip_address=ip_address
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Integrity check failed: Checksum mismatch on stored artifact."
        )

    # Increment counter and log success
    await repo.increment_download_count(release.id)
    await repo.record_download_log(
        release_id=release.id,
        user_id=user_id,
        organization_id=org_id,
        download_status="success",
        client_platform=client_platform,
        request_id=request_id,
        ip_address=ip_address
    )
    await db.commit()

    filename = release.artifact_filename or f"fluentmeet-ai-v{release.version}.zip"

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "application/zip",
        "Content-Length": str(len(artifact_bytes)),
        "ETag": f'"{calculated_sha}"',
        "Cache-Control": "public, max-age=3600, immutable",
        "X-Release-Version": release.version,
        "X-Release-Channel": release.channel,
        "X-SHA256-Checksum": calculated_sha,
    }

    return Response(
        content=artifact_bytes,
        media_type="application/zip",
        headers=headers
    )
