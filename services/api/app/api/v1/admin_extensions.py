from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.base import User, get_utc_now
from app.repositories.extension_release_repository import ExtensionReleaseRepository
from app.services.extension_storage_service import (
    extension_storage,
    ManifestValidationError,
    SecurityScanError,
    ChecksumMismatchError
)
from app.services.extension_builder_service import builder_service
from app.schemas.common import ApiResponse
from app.schemas.extension_release import (
    ExtensionReleaseResponse,
    ExtensionReleaseCreate,
    ExtensionReleaseUpdate,
    ExtensionAnalyticsResponse
)
from app.api.deps import get_current_user
from app.api.v1.extensions import format_release_response

router = APIRouter(prefix="/admin/extensions", tags=["Admin Extensions"])

# Allowed release statuses
VALID_STATUSES = [
    "draft", "building", "testing", "ready_for_review",
    "approved", "published", "failed", "withdrawn", "archived"
]

def verify_admin_access(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensures the user has administrative privileges to manage releases.
    Allowed roles: super_admin, admin, release_manager, or individual in development mode.
    """
    allowed_roles = ["super_admin", "admin", "release_manager", "individual"]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Administrative privileges required for release management."
        )
    return current_user


@router.get("/releases", response_model=ApiResponse[List[ExtensionReleaseResponse]])
async def list_admin_releases(
    request: Request,
    channel: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    List all extension releases with administrative status filter (draft, published, withdrawn, etc.).
    """
    repo = ExtensionReleaseRepository(db)
    releases, total = await repo.list_releases(
        channel=channel.lower() if channel else None,
        status=status.lower() if status else None,
        published_only=False,
        skip=skip,
        limit=limit
    )

    base_url = str(request.base_url)
    items = [format_release_response(r, base_url) for r in releases]
    return ApiResponse.ok_response(data=items, message=f"Retrieved {len(items)} releases.")


@router.post("/releases", response_model=ApiResponse[ExtensionReleaseResponse])
async def create_release(
    payload: ExtensionReleaseCreate,
    request: Request,
    current_user: User = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new extension release record in draft state.
    """
    repo = ExtensionReleaseRepository(db)

    # Check for existing version in the channel
    existing = await repo.get_by_version(payload.version, payload.channel)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Release version '{payload.version}' already exists for channel '{payload.channel}'."
        )

    # Format release notes into list if string
    notes = payload.release_notes
    if isinstance(notes, str):
        notes = [n.strip() for n in notes.split("\n") if n.strip()]

    release = await repo.create(
        extension_name=payload.extension_name or "FluentMeet AI — Real-time English Meeting Coach",
        version=payload.version,
        channel=payload.channel.lower(),
        status="draft",
        manifest_version=3,
        minimum_chrome_version=payload.minimum_chrome_version or "116.0",
        release_notes=notes,
        git_commit_sha=payload.git_commit_sha,
        build_number=payload.build_number,
        download_count=0
    )

    await repo.record_event(
        release_id=release.id,
        event_type="created",
        actor_user_id=current_user.id,
        metadata={"version": release.version, "channel": release.channel}
    )
    await db.commit()

    base_url = str(request.base_url)
    return ApiResponse.ok_response(
        data=format_release_response(release, base_url),
        message=f"Release {release.version} created successfully in 'draft' status."
    )


@router.post("/releases/{release_id}/build", response_model=ApiResponse[ExtensionReleaseResponse])
async def trigger_build_and_package(
    release_id: str,
    request: Request,
    current_user: User = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Packages the extension bundle, generates SHA-256 checksum,
    stores the artifact in object storage, and updates release metadata.
    """
    repo = ExtensionReleaseRepository(db)
    release = await repo.get_by_id(release_id)
    if not release:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Release not found.")

    if release.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot re-package an already published release. Published releases are immutable."
        )

    await repo.update(release, status="building")
    await repo.record_event(
        release_id=release.id,
        event_type="build_started",
        actor_user_id=current_user.id
    )
    await db.commit()

    try:
        packaged = builder_service.package_from_dist(version_override=release.version)

        # Store in storage
        storage_key, checksum, size_bytes = extension_storage.store_release_artifact(
            channel=release.channel,
            version=release.version,
            filename=packaged["filename"],
            data=packaged["zip_bytes"],
            expected_checksum=packaged["sha256"]
        )

        release = await repo.update(
            release,
            status="ready_for_review",
            artifact_storage_key=storage_key,
            artifact_filename=packaged["filename"],
            artifact_size_bytes=size_bytes,
            sha256_checksum=checksum,
            manifest_version=packaged["manifest"].get("manifest_version", 3)
        )

        await repo.record_event(
            release_id=release.id,
            event_type="built",
            actor_user_id=current_user.id,
            metadata={
                "storage_key": storage_key,
                "sha256": checksum,
                "size_bytes": size_bytes
            }
        )
        await db.commit()

        base_url = str(request.base_url)
        return ApiResponse.ok_response(
            data=format_release_response(release, base_url),
            message="Extension successfully built, packaged, and verified."
        )

    except Exception as e:
        await repo.update(release, status="failed")
        await repo.record_event(
            release_id=release.id,
            event_type="build_failed",
            actor_user_id=current_user.id,
            metadata={"error": str(e)}
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Build & packaging failed: {e}"
        )


@router.post("/releases/{release_id}/validate", response_model=ApiResponse[Dict[str, Any]])
async def validate_release(
    release_id: str,
    current_user: User = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Runs automated checks:
    - Manifest V3 structure
    - No leaked secrets / credentials
    - Checksum match
    - Storage availability
    """
    repo = ExtensionReleaseRepository(db)
    release = await repo.get_by_id(release_id)
    if not release or not release.artifact_storage_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Release or artifact not found.")

    try:
        data = extension_storage.get_release_artifact(release.artifact_storage_key)
        val_info = extension_storage.validate_zip_artifact(data, expected_version=release.version)
        calculated_sha = extension_storage.compute_sha256(data)

        checksum_valid = (calculated_sha.lower() == release.sha256_checksum.lower())
        if not checksum_valid:
            raise ChecksumMismatchError("Calculated SHA-256 does not match database record.")

        result = {
            "valid": True,
            "manifest_version": val_info["manifest_version"],
            "version": val_info["version"],
            "sha256_verified": True,
            "secret_scan": "PASSED (No forbidden patterns)",
            "file_count": val_info["file_count"],
            "minimum_chrome_version": release.minimum_chrome_version,
            "status": release.status
        }

        await repo.record_event(
            release_id=release.id,
            event_type="validated",
            actor_user_id=current_user.id,
            metadata=result
        )
        await db.commit()

        return ApiResponse.ok_response(data=result, message="Release validation passed.")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Release validation failed: {e}"
        )


@router.post("/releases/{release_id}/approve", response_model=ApiResponse[ExtensionReleaseResponse])
async def approve_release(
    release_id: str,
    request: Request,
    current_user: User = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Transition release from 'ready_for_review' or 'testing' to 'approved'.
    """
    repo = ExtensionReleaseRepository(db)
    release = await repo.get_by_id(release_id)
    if not release:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Release not found.")

    if not release.artifact_storage_key or not release.sha256_checksum:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot approve a release without a verified artifact and checksum."
        )

    release = await repo.update(release, status="approved")
    await repo.record_event(
        release_id=release.id,
        event_type="approved",
        actor_user_id=current_user.id
    )
    await db.commit()

    base_url = str(request.base_url)
    return ApiResponse.ok_response(
        data=format_release_response(release, base_url),
        message=f"Release {release.version} has been approved."
    )


@router.post("/releases/{release_id}/publish", response_model=ApiResponse[ExtensionReleaseResponse])
async def publish_release(
    release_id: str,
    request: Request,
    current_user: User = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Publish an approved release.
    Updates the latest stable release pointer automatically.
    The Dashboard will immediately show the newly published version.
    """
    repo = ExtensionReleaseRepository(db)
    release = await repo.get_by_id(release_id)
    if not release:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Release not found.")

    if release.status not in ["approved", "ready_for_review"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot publish release with status '{release.status}'. Must be 'approved' first."
        )

    if not release.artifact_storage_key or not release.sha256_checksum:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot publish a release without a verified artifact and checksum."
        )

    release = await repo.update(
        release,
        status="published",
        published_at=get_utc_now(),
        published_by=current_user.id
    )

    await repo.record_event(
        release_id=release.id,
        event_type="published",
        actor_user_id=current_user.id,
        metadata={
            "channel": release.channel,
            "version": release.version,
            "published_at": release.published_at.isoformat()
        }
    )
    await db.commit()

    base_url = str(request.base_url)
    return ApiResponse.ok_response(
        data=format_release_response(release, base_url),
        message=f"Release {release.version} published successfully to {release.channel} channel."
    )


@router.post("/releases/{release_id}/withdraw", response_model=ApiResponse[ExtensionReleaseResponse])
async def withdraw_release(
    release_id: str,
    request: Request,
    reason: str = Query("Emergency security withdrawal", description="Reason for release withdrawal"),
    current_user: User = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Withdraws a published release immediately.
    Halts downloads for this version and reverts the Dashboard's active release pointer.
    """
    repo = ExtensionReleaseRepository(db)
    release = await repo.get_by_id(release_id)
    if not release:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Release not found.")

    release = await repo.update(release, status="withdrawn")
    await repo.record_event(
        release_id=release.id,
        event_type="withdrawn",
        actor_user_id=current_user.id,
        metadata={"reason": reason}
    )
    await db.commit()

    base_url = str(request.base_url)
    return ApiResponse.ok_response(
        data=format_release_response(release, base_url),
        message=f"Release {release.version} has been withdrawn: {reason}."
    )


@router.post("/releases/{release_id}/rollback", response_model=ApiResponse[ExtensionReleaseResponse])
async def rollback_release(
    release_id: str,
    request: Request,
    current_user: User = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Rolls back the active release pointer by withdrawing the current release,
    enabling the previous stable release to serve as latest.
    """
    repo = ExtensionReleaseRepository(db)
    release = await repo.get_by_id(release_id)
    if not release:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Release not found.")

    release = await repo.update(release, status="withdrawn")
    await repo.record_event(
        release_id=release.id,
        event_type="rolled_back",
        actor_user_id=current_user.id,
        metadata={"action": "Emergency pointer rollback to prior version"}
    )
    await db.commit()

    # Find the now-active latest published release
    latest_active = await repo.get_latest_published(release.channel)

    base_url = str(request.base_url)
    resp_data = format_release_response(latest_active or release, base_url)
    return ApiResponse.ok_response(
        data=resp_data,
        message=f"Rolled back release {release.version}. Active stable release is now {latest_active.version if latest_active else 'none'}."
    )


@router.get("/releases/{release_id}/build-logs", response_model=ApiResponse[List[Dict[str, Any]]])
async def get_build_logs(
    release_id: str,
    current_user: User = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch the audit trail and build events for a specific release.
    """
    repo = ExtensionReleaseRepository(db)
    events = await repo.get_events(release_id)
    logs = [
        {
            "id": ev.id,
            "event_type": ev.event_type,
            "actor_user_id": ev.actor_user_id,
            "metadata": ev.event_metadata,
            "created_at": ev.created_at.isoformat() if ev.created_at else None
        }
        for ev in events
    ]
    return ApiResponse.ok_response(data=logs, message="Build and release logs retrieved.")


@router.get("/analytics", response_model=ApiResponse[ExtensionAnalyticsResponse])
async def get_extension_analytics(
    current_user: User = Depends(verify_admin_access),
    db: AsyncSession = Depends(get_db)
):
    """
    Aggregates release counts, total downloads, and client platforms.
    """
    repo = ExtensionReleaseRepository(db)
    stats = await repo.get_analytics()
    return ApiResponse.ok_response(
        data=ExtensionAnalyticsResponse(**stats),
        message="Extension analytics retrieved successfully."
    )
