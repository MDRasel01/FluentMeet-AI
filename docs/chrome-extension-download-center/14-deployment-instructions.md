# Deployment Instructions — Chrome Extension Distribution & Release System

## 1. Prerequisites

- **Python:** 3.11+
- **Node.js:** 20+
- **Package Manager:** `pnpm` 9+
- **Database:** PostgreSQL 15+ (or SQLite for development)
- **Object Storage Directory:** Readable and writable path for release artifacts (defaults to `storage/releases/`).

---

## 2. Backend Database Migration

Run the Alembic migration to create `extension_releases`, `extension_download_logs`, and `extension_release_events`:

```bash
cd services/api
alembic upgrade head
```

Verify that revision `004_extension_releases` has been applied successfully.

---

## 3. Building the Extension Production Package

To generate the initial production release artifact:

```bash
# 1. Build the extension bundle
cd apps/extension
pnpm install
pnpm build

# 2. Package the extension and generate SHA-256 checksum
cd ../..
python scripts/package_extension.py --channel stable --out-dir storage/releases
```

This will produce:
- `storage/releases/stable/1.0.0/fluentmeet-ai-v1.0.0.zip`
- `storage/releases/stable/1.0.0/checksum.sha256`
- `storage/releases/stable/1.0.0/release-manifest.json`

---

## 4. Registering & Publishing the Initial Release via Admin API

Using `curl` or the Super Admin console:

```bash
# 1. Create Draft Release
curl -X POST http://localhost:8000/api/v1/admin/extensions/releases \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "1.0.0",
    "channel": "stable",
    "minimum_chrome_version": "116.0",
    "release_notes": [
      "Initial production release of FluentMeet AI Coach",
      "Real-time dual-track speech coaching for Google Meet, Zoom, and MS Teams",
      "Live speaking pace, filler word detection, and pronunciation scoring"
    ]
  }'

# 2. Package & Store Artifact
curl -X POST http://localhost:8000/api/v1/admin/extensions/releases/<RELEASE_ID>/build \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>"

# 3. Approve Release
curl -X POST http://localhost:8000/api/v1/admin/extensions/releases/<RELEASE_ID>/approve \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>"

# 4. Publish Release
curl -X POST http://localhost:8000/api/v1/admin/extensions/releases/<RELEASE_ID>/publish \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>"
```

---

## 5. Starting the Web Dashboard & API

### Start FastAPI Backend:
```bash
cd services/api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Web Dashboard:
```bash
cd apps/dashboard
pnpm dev
```
Open [http://localhost:3000](http://localhost:3000) and click **Chrome Extension** in the sidebar.

### Start Interactive Workbench (All 3 Core Interfaces):
```bash
cd FluentMeet-AI
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to toggle between **Web Dashboard**, **Chrome Extension Side Panel**, **Super Admin Console**, and **Design System Showcase**.

