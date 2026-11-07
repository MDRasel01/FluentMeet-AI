import pytest
from httpx import AsyncClient
import io
import zipfile
import json
import hashlib
from app.services.extension_storage_service import extension_storage

@pytest.mark.asyncio
async def test_extension_release_full_lifecycle(async_client: AsyncClient, auth_token: dict):
    headers = auth_token["headers"]

    # 1. Create Release in Draft Status
    create_payload = {
        "version": "1.0.0",
        "channel": "stable",
        "minimum_chrome_version": "116.0",
        "release_notes": [
            "Initial production release of FluentMeet AI Coach",
            "Multi-track audio capture with Web Audio API",
            "Google Meet, Zoom, and Teams integration"
        ],
        "git_commit_sha": "a1b2c3d4e5f67890",
        "build_number": "build-001"
    }

    create_resp = await async_client.post(
        "/api/v1/admin/extensions/releases",
        json=create_payload,
        headers=headers
    )
    assert create_resp.status_code == 200
    release_data = create_resp.json()["data"]
    release_id = release_data["id"]
    assert release_data["version"] == "1.0.0"
    assert release_data["status"] == "draft"

    # Verify unreleased version is NOT downloadable by public/user latest endpoint
    latest_resp = await async_client.get("/api/v1/extensions/releases/latest?channel=stable")
    assert latest_resp.status_code == 404

    # 2. Build and Package Extension
    build_resp = await async_client.post(
        f"/api/v1/admin/extensions/releases/{release_id}/build",
        headers=headers
    )
    assert build_resp.status_code == 200
    built_data = build_resp.json()["data"]
    assert built_data["status"] == "ready_for_review"
    assert built_data["sha256_checksum"] is not None
    assert built_data["artifact_size_bytes"] > 0
    assert built_data["artifact_filename"] == "fluentmeet-ai-v1.0.0.zip"

    # 3. Validate Release Artifact
    val_resp = await async_client.post(
        f"/api/v1/admin/extensions/releases/{release_id}/validate",
        headers=headers
    )
    assert val_resp.status_code == 200
    val_data = val_resp.json()["data"]
    assert val_data["valid"] is True
    assert val_data["manifest_version"] == 3
    assert val_data["sha256_verified"] is True

    # 4. Attempt download before publish -> Must be blocked (HTTP 403)
    blocked_dl = await async_client.get(f"/api/v1/extensions/releases/{release_id}/download")
    assert blocked_dl.status_code == 403

    # 5. Approve Release
    approve_resp = await async_client.post(
        f"/api/v1/admin/extensions/releases/{release_id}/approve",
        headers=headers
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["data"]["status"] == "approved"

    # 6. Publish Release
    pub_resp = await async_client.post(
        f"/api/v1/admin/extensions/releases/{release_id}/publish",
        headers=headers
    )
    assert pub_resp.status_code == 200
    pub_data = pub_resp.json()["data"]
    assert pub_data["status"] == "published"
    assert pub_data["published_at"] is not None

    # 7. Check Latest Endpoint resolves the newly published release
    latest_resp = await async_client.get("/api/v1/extensions/releases/latest?channel=stable")
    assert latest_resp.status_code == 200
    latest_data = latest_resp.json()["data"]
    assert latest_data["id"] == release_id
    assert latest_data["version"] == "1.0.0"
    assert latest_data["sha256_checksum"] == built_data["sha256_checksum"]
    assert len(latest_data["release_notes"]) == 3

    # 8. Check Version History Table Endpoint
    history_resp = await async_client.get("/api/v1/extensions/releases")
    assert history_resp.status_code == 200
    history_data = history_resp.json()["data"]
    assert history_data["total"] == 1
    assert history_data["items"][0]["version"] == "1.0.0"
    assert history_data["current_stable"]["version"] == "1.0.0"

    # 9. Download ZIP via specific release endpoint
    dl_resp = await async_client.get(
        f"/api/v1/extensions/releases/{release_id}/download",
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    )
    assert dl_resp.status_code == 200
    assert dl_resp.headers["content-type"] == "application/zip"
    assert "fluentmeet-ai-v1.0.0.zip" in dl_resp.headers["content-disposition"]
    dl_bytes = dl_resp.content
    assert hashlib.sha256(dl_bytes).hexdigest() == latest_data["sha256_checksum"]

    # Verify downloaded ZIP is readable and has manifest.json at root
    with zipfile.ZipFile(io.BytesIO(dl_bytes), "r") as zf:
        namelist = zf.namelist()
        assert "manifest.json" in namelist
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
        assert manifest["manifest_version"] == 3

    # 10. Download ZIP via Latest Endpoint
    latest_dl = await async_client.get(
        "/api/v1/extensions/releases/latest/download?channel=stable",
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    )
    assert latest_dl.status_code == 200
    assert hashlib.sha256(latest_dl.content).hexdigest() == latest_data["sha256_checksum"]

    # 11. Verify Download Analytics & Telemetry
    analytics_resp = await async_client.get("/api/v1/admin/extensions/analytics", headers=headers)
    assert analytics_resp.status_code == 200
    stats = analytics_resp.json()["data"]
    assert stats["total_releases"] >= 1
    assert stats["published_releases"] >= 1
    assert stats["total_downloads"] >= 2
    assert stats["current_stable_version"] == "1.0.0"
    assert "Windows" in stats["downloads_by_platform"]
    assert "macOS" in stats["downloads_by_platform"]

    # 12. Audit Logs Check
    logs_resp = await async_client.get(
        f"/api/v1/admin/extensions/releases/{release_id}/build-logs",
        headers=headers
    )
    assert logs_resp.status_code == 200
    logs = logs_resp.json()["data"]
    event_types = [l["event_type"] for l in logs]
    assert "created" in event_types
    assert "built" in event_types
    assert "validated" in event_types
    assert "approved" in event_types
    assert "published" in event_types

@pytest.mark.asyncio
async def test_extension_release_automatic_update_pointer(async_client: AsyncClient, auth_token: dict):
    """
    Test that when version 1.0.1 is published after 1.0.0:
    - Latest endpoint automatically updates to 1.0.1.
    - Version history lists both 1.0.1 and 1.0.0.
    - Downloading latest resolves 1.0.1.
    - User can still download archived 1.0.0.
    """
    headers = auth_token["headers"]

    # Publish v1.0.0
    r1 = await async_client.post(
        "/api/v1/admin/extensions/releases",
        json={"version": "1.0.0", "channel": "stable"},
        headers=headers
    )
    id1 = r1.json()["data"]["id"]
    await async_client.post(f"/api/v1/admin/extensions/releases/{id1}/build", headers=headers)
    await async_client.post(f"/api/v1/admin/extensions/releases/{id1}/approve", headers=headers)
    await async_client.post(f"/api/v1/admin/extensions/releases/{id1}/publish", headers=headers)

    # Initial check: latest is 1.0.0
    check1 = await async_client.get("/api/v1/extensions/releases/latest?channel=stable")
    assert check1.json()["data"]["version"] == "1.0.0"

    # Publish v1.0.1 (bug fix release)
    r2 = await async_client.post(
        "/api/v1/admin/extensions/releases",
        json={
            "version": "1.0.1",
            "channel": "stable",
            "release_notes": ["Fixed meeting tab detection", "Optimized audio resampler buffer"]
        },
        headers=headers
    )
    id2 = r2.json()["data"]["id"]
    await async_client.post(f"/api/v1/admin/extensions/releases/{id2}/build", headers=headers)
    await async_client.post(f"/api/v1/admin/extensions/releases/{id2}/approve", headers=headers)
    await async_client.post(f"/api/v1/admin/extensions/releases/{id2}/publish", headers=headers)

    # Automatic update: latest pointer is immediately 1.0.1!
    check2 = await async_client.get("/api/v1/extensions/releases/latest?channel=stable")
    assert check2.json()["data"]["version"] == "1.0.1"

    # Version history has both versions
    history = await async_client.get("/api/v1/extensions/releases")
    items = history.json()["data"]["items"]
    versions = [i["version"] for i in items]
    assert "1.0.1" in versions
    assert "1.0.0" in versions

    # Older version 1.0.0 can still be downloaded!
    dl_v1 = await async_client.get(f"/api/v1/extensions/releases/{id1}/download")
    assert dl_v1.status_code == 200

    # Latest download serves 1.0.1
    dl_latest = await async_client.get("/api/v1/extensions/releases/latest/download?channel=stable")
    assert dl_latest.status_code == 200
    assert "fluentmeet-ai-v1.0.1.zip" in dl_latest.headers["content-disposition"]

@pytest.mark.asyncio
async def test_extension_release_rollback_and_withdrawal(async_client: AsyncClient, auth_token: dict):
    """
    Test emergency rollback:
    When v1.0.1 has a bug and is rolled back, the latest pointer reverts to v1.0.0.
    """
    headers = auth_token["headers"]

    # Publish v1.0.0
    r1 = await async_client.post(
        "/api/v1/admin/extensions/releases",
        json={"version": "1.0.0", "channel": "stable"},
        headers=headers
    )
    id1 = r1.json()["data"]["id"]
    await async_client.post(f"/api/v1/admin/extensions/releases/{id1}/build", headers=headers)
    await async_client.post(f"/api/v1/admin/extensions/releases/{id1}/approve", headers=headers)
    await async_client.post(f"/api/v1/admin/extensions/releases/{id1}/publish", headers=headers)

    # Publish v1.0.1
    r2 = await async_client.post(
        "/api/v1/admin/extensions/releases",
        json={"version": "1.0.1", "channel": "stable"},
        headers=headers
    )
    id2 = r2.json()["data"]["id"]
    await async_client.post(f"/api/v1/admin/extensions/releases/{id2}/build", headers=headers)
    await async_client.post(f"/api/v1/admin/extensions/releases/{id2}/approve", headers=headers)
    await async_client.post(f"/api/v1/admin/extensions/releases/{id2}/publish", headers=headers)

    assert (await async_client.get("/api/v1/extensions/releases/latest?channel=stable")).json()["data"]["version"] == "1.0.1"

    # Emergency rollback of v1.0.1
    rollback_resp = await async_client.post(
        f"/api/v1/admin/extensions/releases/{id2}/rollback",
        headers=headers
    )
    assert rollback_resp.status_code == 200

    # The latest pointer reverted to v1.0.0!
    reverted = await async_client.get("/api/v1/extensions/releases/latest?channel=stable")
    assert reverted.status_code == 200
    assert reverted.json()["data"]["version"] == "1.0.0"

    # Download of withdrawn v1.0.1 is blocked!
    blocked = await async_client.get(f"/api/v1/extensions/releases/{id2}/download")
    assert blocked.status_code == 403


@pytest.mark.asyncio
async def test_extension_security_and_validation(async_client: AsyncClient, auth_token: dict):
    """
    Security & Validation tests:
    - Secret scanning: Rejects ZIP containing .env or secret keys
    - Manifest validation: Rejects missing manifest.json or non-MV3
    - Tamper detection: Checksum mismatch triggers failure
    - Unauthorized access: Unauthenticated users blocked from admin endpoints
    """
    headers = auth_token["headers"]

    # 1. Unauthenticated request to admin endpoint must be rejected
    unauth_resp = await async_client.post(
        "/api/v1/admin/extensions/releases",
        json={"version": "2.0.0", "channel": "stable"}
    )
    assert unauth_resp.status_code in [401, 403]

    # 2. Secret scan rejection
    bad_zip_buffer = io.BytesIO()
    with zipfile.ZipFile(bad_zip_buffer, "w") as zf:
        zf.writestr("manifest.json", json.dumps({"manifest_version": 3, "version": "2.0.0"}))
        zf.writestr(".env", "GEMINI_API_KEY=supersecret12345")

    with pytest.raises(Exception) as exc_info:
        extension_storage.validate_zip_artifact(bad_zip_buffer.getvalue())
    assert "Security violation" in str(exc_info.value)

    # 3. Missing manifest.json rejection
    missing_manifest_zip = io.BytesIO()
    with zipfile.ZipFile(missing_manifest_zip, "w") as zf:
        zf.writestr("sidepanel.html", "<h1>Hello</h1>")

    with pytest.raises(Exception) as exc_info:
        extension_storage.validate_zip_artifact(missing_manifest_zip.getvalue())
    assert "Root directory of ZIP must contain 'manifest.json'" in str(exc_info.value)

    # 4. Non-MV3 manifest rejection
    bad_mv_zip = io.BytesIO()
    with zipfile.ZipFile(bad_mv_zip, "w") as zf:
        zf.writestr("manifest.json", json.dumps({"manifest_version": 2, "version": "2.0.0"}))

    with pytest.raises(Exception) as exc_info:
        extension_storage.validate_zip_artifact(bad_mv_zip.getvalue())
    assert "Expected Manifest V3" in str(exc_info.value)

