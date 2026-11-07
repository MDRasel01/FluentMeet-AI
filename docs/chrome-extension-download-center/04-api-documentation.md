# API Documentation — Chrome Extension Distribution & Version Management

Base Prefix: `/api/v1`

---

## 1. Public & Authenticated User APIs

### 1.1 Get Latest Release
Retrieves latest published release metadata for a designated channel.

- **Method / Path:** `GET /api/v1/extensions/releases/latest?channel=stable`
- **Authentication:** Public or Optional Bearer Token
- **Query Parameters:**
  - `channel` (string, optional, default: `"stable"`): `stable`, `beta`, `internal`
- **Response `200 OK`:**
```json
{
  "success": true,
  "data": {
    "id": "c1f7a0b2-4d8e-4a11-b3c9-9f201b8e4f50",
    "extension_name": "FluentMeet AI — Real-time English Meeting Coach",
    "version": "1.0.0",
    "channel": "stable",
    "status": "published",
    "manifest_version": 3,
    "build_number": "build-20261107-001",
    "git_commit_sha": "7f9a2b1",
    "release_notes": [
      "Real-time dual-track speech coaching for Google Meet, Zoom, and Teams",
      "Manifest V3 Side Panel API integration",
      "Live speaking pace (WPM), filler word detection, and pronunciation scoring"
    ],
    "minimum_chrome_version": "116.0",
    "artifact_filename": "fluentmeet-ai-v1.0.0.zip",
    "artifact_size_bytes": 98300,
    "sha256_checksum": "53e8620c9422f7e7f7a2715eaccc7a37bca41b87ca2f5a4f774a5dc7480cf003",
    "download_count": 142,
    "download_url": "https://api.fluentmeet.ai/api/v1/extensions/releases/c1f7a0b2.../download",
    "published_at": "2026-11-07T10:00:00Z",
    "created_at": "2026-11-07T09:30:00Z",
    "updated_at": "2026-11-07T10:00:00Z"
  },
  "message": "Latest stable release retrieved successfully."
}
```

---

### 1.2 Get Version History
Retrieves paginated version history of published releases for the Dashboard Version History table.

- **Method / Path:** `GET /api/v1/extensions/releases`
- **Query Parameters:**
  - `channel` (string, optional): Filter by channel
  - `skip` (integer, default: 0)
  - `limit` (integer, default: 50, max: 100)
- **Response `200 OK`:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "rel-v1.0.1",
        "version": "1.0.1",
        "channel": "stable",
        "status": "published",
        "artifact_size_bytes": 98450,
        "sha256_checksum": "...",
        "published_at": "2026-11-07T14:00:00Z"
      },
      {
        "id": "rel-v1.0.0",
        "version": "1.0.0",
        "channel": "stable",
        "status": "published",
        "artifact_size_bytes": 98300,
        "sha256_checksum": "...",
        "published_at": "2026-11-07T10:00:00Z"
      }
    ],
    "total": 2,
    "current_stable": {
      "version": "1.0.1",
      "status": "published"
    }
  },
  "message": "Version history retrieved successfully."
}
```

---

### 1.3 Download Latest Published Release
Resolves the active published stable release dynamically on the backend and streams the ZIP file directly.

- **Method / Path:** `GET /api/v1/extensions/releases/latest/download?channel=stable`
- **Response Headers:**
  - `Content-Disposition: attachment; filename="fluentmeet-ai-v1.0.0.zip"`
  - `Content-Type: application/zip`
  - `ETag: "53e8620c9422f7e7f7a2715eaccc7a37bca41b87ca2f5a4f774a5dc7480cf003"`
  - `X-Release-Version: 1.0.0`
  - `X-SHA256-Checksum: 53e8620c9422f7e7f7a2715eaccc7a37bca41b87ca2f5a4f774a5dc7480cf003`

---

### 1.4 Download Specific Release
Downloads a specific archived version from the version history table.

- **Method / Path:** `GET /api/v1/extensions/releases/{release_id}/download`
- **Access Rule:** Only published releases can be downloaded. If the release is in `draft`, `building`, `failed`, or `withdrawn` state, access returns `HTTP 403 Forbidden`.

---

## 2. Super Admin Release Management APIs

All admin endpoints require administrative authentication (`Bearer <JWT>`) with roles `super_admin`, `admin`, or `release_manager`.

### 2.1 List All Releases (Admin)
- **Method / Path:** `GET /api/v1/admin/extensions/releases`
- **Query Parameters:** `channel`, `status`, `skip`, `limit`
- **Description:** Returns all releases regardless of status (including drafts, building, and withdrawn).

### 2.2 Create Release
- **Method / Path:** `POST /api/v1/admin/extensions/releases`
- **Request Body:**
```json
{
  "version": "1.0.1",
  "channel": "stable",
  "minimum_chrome_version": "116.0",
  "git_commit_sha": "a1b2c3d",
  "build_number": "build-002",
  "release_notes": [
    "Improved audio streaming stability during network jitter",
    "Optimized audio resampler ring buffer"
  ]
}
```

### 2.3 Trigger Build & Packaging
- **Method / Path:** `POST /api/v1/admin/extensions/releases/{id}/build`
- **Description:** Packages the extension bundle, enforces secret scanning, writes `manifest.json` at root, calculates SHA-256, and stores artifact in object storage. Transitions release to `ready_for_review`.

### 2.4 Validate Release
- **Method / Path:** `POST /api/v1/admin/extensions/releases/{id}/validate`
- **Description:** Checks Manifest V3 compliance, verifies checksum match against storage, and confirms absence of leaked secrets.

### 2.5 Approve Release
- **Method / Path:** `POST /api/v1/admin/extensions/releases/{id}/approve`
- **Description:** Transitions release from `ready_for_review` to `approved`.

### 2.6 Publish Release
- **Method / Path:** `POST /api/v1/admin/extensions/releases/{id}/publish`
- **Description:** Transitions release to `published`. Sets `published_at` to current timestamp. Updates active pointer so all user queries immediately resolve the new version.

### 2.7 Emergency Withdrawal
- **Method / Path:** `POST /api/v1/admin/extensions/releases/{id}/withdraw?reason=Security%20Patch`
- **Description:** Withdraws a published version immediately. Halts downloads and blocks access.

### 2.8 Rollback Release
- **Method / Path:** `POST /api/v1/admin/extensions/releases/{id}/rollback`
- **Description:** Withdraws the active version and automatically falls back to the previous published release.

### 2.9 Get Release Audit Logs
- **Method / Path:** `GET /api/v1/admin/extensions/releases/{id}/build-logs`

### 2.10 Download Analytics
- **Method / Path:** `GET /api/v1/admin/extensions/analytics`
- **Response:**
```json
{
  "success": true,
  "data": {
    "total_releases": 4,
    "published_releases": 2,
    "total_downloads": 184,
    "current_stable_version": "1.0.0",
    "downloads_by_platform": {
      "Windows": 112,
      "macOS": 58,
      "Linux": 14
    },
    "downloads_by_version": {
      "1.0.0": 142,
      "0.9.5": 42
    },
    "recent_downloads": [...]
  }
}
```

