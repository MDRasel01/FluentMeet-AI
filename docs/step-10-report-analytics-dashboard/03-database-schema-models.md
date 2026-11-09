# Step 10 — Database Schema & Data Models Specification

**Module:** Database & Storage Layer  
**Migration:** `006_report_engine_schema.py`  
**Models:** `app.models.report`  

---

## 1. Schema Tables

### 1.1 `report_snapshots`
Stores immutable, versioned report payloads for meetings and individual participants.

| Column | Type | Nullable | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | No | Primary Key (UUIDv4) |
| `tenant_id` | VARCHAR(36) | Yes | Foreign Key to `organizations.id` (Indexed) |
| `meeting_id` | VARCHAR(36) | No | Foreign Key to `meetings.id` (CASCADE, Indexed) |
| `report_type` | VARCHAR(32) | No | `'meeting_summary'` or `'individual_participant'` |
| `participant_id` | VARCHAR(36) | Yes | Foreign Key to `meeting_participants.id` |
| `speaker_label` | VARCHAR(64) | Yes | Diarized label e.g. `'speaker_alice'` |
| `report_version` | INTEGER | No | Incremental version number (default `1`) |
| `report_status` | VARCHAR(32) | No | `'completed'`, `'partial'`, `'insufficient_evidence'` |
| `source_analysis_version` | VARCHAR(32) | No | Upstream analysis contract version (`'1.0'`) |
| `scoring_rubric_version` | VARCHAR(32) | No | Scoring weighting rubric version (`'1.0'`) |
| `overall_score` | FLOAT | Yes | Calibrated score or `NULL` if unavailable |
| `confidence_score` | FLOAT | Yes | Blended model confidence score `[0.0, 1.0]` |
| `word_count` | INTEGER | No | Total evaluated words |
| `speaking_duration_seconds` | FLOAT | No | Vocal speech elapsed seconds |
| `report_payload` | JSON | No | Full structured immutable JSON document |
| `generated_at` | TIMESTAMP WITH TZ | No | Generation timestamp |
| `created_by` | VARCHAR(36) | Yes | User ID of requester |

### 1.2 `report_exports`
Tracks generated and exported report files (PDF, CSV, HTML).

| Column | Type | Nullable | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | No | Primary Key (UUIDv4) |
| `tenant_id` | VARCHAR(36) | Yes | Foreign Key to `organizations.id` |
| `user_id` | VARCHAR(36) | Yes | User ID of exporter |
| `report_snapshot_id` | VARCHAR(36) | No | Foreign Key to `report_snapshots.id` (CASCADE) |
| `export_format` | VARCHAR(16) | No | `'pdf'`, `'csv'`, or `'html'` |
| `storage_reference` | VARCHAR(512) | Yes | Storage URI or memory reference |
| `export_status` | VARCHAR(32) | No | `'completed'`, `'pending'`, `'failed'` |
| `file_size_bytes` | INTEGER | Yes | Size of exported file |
| `content_hash` | VARCHAR(64) | Yes | SHA-256 integrity hash of document |
| `expires_at` | TIMESTAMP WITH TZ | Yes | Artifact retention expiry |

### 1.3 `report_access_logs`
Audit and compliance tracking for report interactions.

| Column | Type | Nullable | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | No | Primary Key (UUIDv4) |
| `tenant_id` | VARCHAR(36) | Yes | Tenant context |
| `report_snapshot_id` | VARCHAR(36) | No | Foreign Key to `report_snapshots.id` |
| `actor_id` | VARCHAR(36) | Yes | User ID performing the action |
| `action` | VARCHAR(32) | No | `'view'`, `'export_csv'`, `'export_html'`, `'generate_reports'` |
| `request_metadata` | JSON | Yes | Metadata (file size, version, IP address) |
| `created_at` | TIMESTAMP WITH TZ | No | Access timestamp |
