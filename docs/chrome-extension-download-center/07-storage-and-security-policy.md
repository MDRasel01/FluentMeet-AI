# Storage & Security Policy

## 1. Storage Topology & Organization

Binary ZIP archives are **never** stored inside the PostgreSQL relational database. Artifacts reside in private, durable, S3-compatible or local durable object storage with immutable version paths:

```
storage/releases/
├── stable/
│   ├── 1.0.0/
│   │   ├── fluentmeet-ai-v1.0.0.zip
│   │   ├── checksum.sha256
│   │   └── release-manifest.json
│   └── 1.0.1/
│       ├── fluentmeet-ai-v1.0.1.zip
│       ├── checksum.sha256
│       └── release-manifest.json
└── beta/
    └── 1.1.0-beta.1/
        ├── fluentmeet-ai-v1.1.0-beta.1.zip
        ├── checksum.sha256
        └── release-manifest.json
```

---

## 2. Integrity & Tamper Detection

1. **SHA-256 Checksum Calculation**:
   - Calculated during packaging and written to the database column `sha256_checksum`.
   - Written to disk as `checksum.sha256`.
2. **Download-Time Verification**:
   - Every time a user initiates a download via `/api/v1/extensions/releases/{id}/download` or `/api/v1/extensions/releases/latest/download`, the server recomputes the SHA-256 hash of the artifact on the fly before streaming.
   - If the hash differs from the database record, download is halted with `HTTP 500` and flagged as `blocked` in `extension_download_logs`.
3. **Immutability of Published Releases**:
   - Once a release status transitions to `published`, the backend rejects any re-build or modification requests (`HTTP 400`).
   - Updates must be delivered under a new higher version number.

---

## 3. Secret Leakage Prevention & Scanning Rules

The packaging pipeline enforces strict secret scanning. If any of the following patterns are found in the bundle, the packaging process fails immediately:
- `.env`, `.env.local`, `.env.production`
- `.pem`, `.key`, `id_rsa`, `id_ed25519`
- `client_secret*.json`, `service_account*.json`
- `credentials.json`, `token.json`

### Client-Side Extension Code Sensitivity Warning:
Chrome extension bundles execute in the client's local browser and can be unpacked and inspected by end users. Consequently:
- **No private signing keys** are stored in the ZIP or repo.
- **No Gemini API keys** or AI model secrets are bundled.
- **No backend administrative credentials** are included.
- All AI and transcription queries route through authenticated FastAPI backend services.

---

## 4. Download Authorization & Signed Tokens

- Public releases can be downloaded directly from the Dashboard.
- Short-lived signed download tokens (`generate_signed_download_token`) with a 5-minute expiry can be generated for secure third-party or programmatic downloads.
- Failed or withdrawn releases return `HTTP 403 Forbidden`.

