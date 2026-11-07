# Database Schema — Chrome Extension Version & Release Management

## 1. Relational Entity Relationship Diagram

```
+------------------------------------+          +------------------------------------+
|         extension_releases         |          |                users               |
+------------------------------------+          +------------------------------------+
| id (PK, String 36)                 |          | id (PK, String 36)                 |
| extension_name (String 255)        |          | email (String 255)                 |
| version (String 32, SemVer)        |          | full_name (String 255)             |
| channel (String 32)                |          | role (String 50)                   |
| status (String 32)                 |          +------------------------------------+
| manifest_version (Integer)         |                             ^
| build_number (String 64)           |                             |
| git_commit_sha (String 64)         |                             |
| release_notes (JSON)               |                             |
| minimum_chrome_version (String 32) |                             |
| artifact_storage_key (String 512)  |                             |
| artifact_filename (String 255)     |                             |
| artifact_size_bytes (Integer)      |                             |
| sha256_checksum (String 64)        |                             |
| download_count (Integer)           |                             |
| published_at (DateTime TZ)         |                             |
| published_by (FK -> users.id) -----+-----------------------------+
| created_at (DateTime TZ)           |
| updated_at (DateTime TZ)           |
+------------------------------------+
         |                      |
         | 1:N                  | 1:N
         v                      v
+-----------------------------+ +-----------------------------+
|   extension_download_logs   | |  extension_release_events   |
+-----------------------------+ +-----------------------------+
| id (PK, String 36)          | | id (PK, String 36)          |
| release_id (FK, CASCADE)    | | release_id (FK, CASCADE)    |
| user_id (FK -> users.id)    | | event_type (String 64)      |
| organization_id (FK)        | | actor_user_id (FK)          |
| downloaded_at (DateTime TZ) | | event_metadata (JSON)       |
| download_status (String 32) | | created_at (DateTime TZ)    |
| client_platform (String 64) | +-----------------------------+
| request_id (String 64)      |
| ip_address (String 45)      |
+-----------------------------+
```

---

## 2. Table Definitions

### 2.1 `extension_releases`
Stores official release artifacts, verification metadata, and lifecycle state.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `VARCHAR(36)` | No | `UUIDv4` | Unique release identifier |
| `extension_name` | `VARCHAR(255)` | No | `'FluentMeet AI...'` | Name of the extension |
| `version` | `VARCHAR(32)` | No | - | Semantic version string (e.g. `1.0.0`) |
| `channel` | `VARCHAR(32)` | No | `'stable'` | Channel: `stable`, `beta`, `internal` |
| `status` | `VARCHAR(32)` | No | `'draft'` | Lifecycle status |
| `manifest_version` | `INTEGER` | No | `3` | Chrome extension manifest version |
| `build_number` | `VARCHAR(64)` | Yes | `NULL` | Internal CI/CD build number |
| `git_commit_sha` | `VARCHAR(64)` | Yes | `NULL` | Git commit hash |
| `release_notes` | `JSON` | Yes | `NULL` | Array of changelog bullet points |
| `minimum_chrome_version` | `VARCHAR(32)` | No | `'116.0'` | Minimum supported Chrome browser |
| `artifact_storage_key` | `VARCHAR(512)` | Yes | `NULL` | Storage key in object store |
| `artifact_filename` | `VARCHAR(255)` | Yes | `NULL` | Name of downloadable ZIP file |
| `artifact_size_bytes` | `INTEGER` | No | `0` | Byte length of ZIP archive |
| `sha256_checksum` | `VARCHAR(64)` | Yes | `NULL` | 64-char hex SHA-256 integrity hash |
| `download_count` | `INTEGER` | No | `0` | Cumulative successful downloads |
| `published_at` | `TIMESTAMP WITH TZ`| Yes | `NULL` | Timestamp when published to users |
| `published_by` | `VARCHAR(36)` | Yes | `NULL` | Admin user ID who authorized publish |
| `created_at` | `TIMESTAMP WITH TZ`| No | `NOW()` | Creation timestamp |
| `updated_at` | `TIMESTAMP WITH TZ`| No | `NOW()` | Last state update timestamp |

**Indexes & Constraints:**
- `uq_extension_release_channel_version`: UNIQUE (`channel`, `version`)
- `ix_extension_releases_version`: INDEX (`version`)
- `ix_extension_releases_channel`: INDEX (`channel`)
- `ix_extension_releases_status`: INDEX (`status`)
- `ix_extension_releases_channel_status`: INDEX (`channel`, `status`)
- `ix_extension_releases_published_at`: INDEX (`published_at`)

### 2.2 `extension_download_logs`
Tracks download telemetry, client operating systems, and verification status without storing unnecessary PII.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `VARCHAR(36)` | No | `UUIDv4` | Unique log entry ID |
| `release_id` | `VARCHAR(36)` | No | - | Foreign key to `extension_releases.id` (ON DELETE CASCADE) |
| `user_id` | `VARCHAR(36)` | Yes | `NULL` | Authenticated user ID (if logged in) |
| `organization_id` | `VARCHAR(36)` | Yes | `NULL` | Scoped tenant ID |
| `downloaded_at` | `TIMESTAMP WITH TZ`| No | `NOW()` | Download timestamp |
| `download_status` | `VARCHAR(32)` | No | `'success'` | `success`, `failed`, `blocked` |
| `client_platform` | `VARCHAR(64)` | No | `'Unknown'` | Operating system (`Windows`, `macOS`, etc.) |
| `request_id` | `VARCHAR(64)` | Yes | `NULL` | Request tracing ID |
| `ip_address` | `VARCHAR(45)` | Yes | `NULL` | Anonymized client IP |

**Indexes:**
- `ix_extension_download_logs_release_id`: INDEX (`release_id`)
- `ix_extension_download_logs_user_id`: INDEX (`user_id`)
- `ix_extension_download_logs_downloaded_at`: INDEX (`downloaded_at`)

### 2.3 `extension_release_events`
Audit trail recording all administrative release actions.

| Column | Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | `VARCHAR(36)` | No | `UUIDv4` | Unique event ID |
| `release_id` | `VARCHAR(36)` | No | - | Foreign key to `extension_releases.id` (ON DELETE CASCADE) |
| `event_type` | `VARCHAR(64)` | No | - | `created`, `built`, `validated`, `approved`, `published`, `withdrawn`, `rolled_back` |
| `actor_user_id` | `VARCHAR(36)` | Yes | `NULL` | User ID of executing admin |
| `event_metadata`| `JSON` | Yes | `NULL` | Structured metadata parameters |
| `created_at` | `TIMESTAMP WITH TZ`| No | `NOW()` | Event timestamp |

---

## 3. Database Migration

The schema is registered and managed via Alembic:
`services/api/migrations/versions/004_extension_releases.py`  
- Revises: `003_transcript_diarization`
- Provides clean, reversible `upgrade()` and `downgrade()` logic.

