# Release Workflow & Lifecycle State Machine

## 1. Release State Machine

Every Chrome Extension release follows a deterministic lifecycle:

```
                  +---------+
                  |  DRAFT  |
                  +---------+
                       |
                       | [Trigger Build]
                       v
                 +----------+
                 | BUILDING |
                 +----------+
                  /        \
   (Build Failure)          (Build Success)
        /                     \
       v                       v
  +--------+          +------------------+
  | FAILED |          | READY_FOR_REVIEW |
  +--------+          +------------------+
                               |
                               | [Validate & Approve]
                               v
                         +----------+
                         | APPROVED |
                         +----------+
                               |
                               | [Publish]
                               v
                        +-----------+
            +---------> | PUBLISHED | <----------- Active Pointer on Dashboard
            |           +-----------+
            |                 |
     (New Version)     (Emergency Bug/Vulnerability)
            |                 |
            v                 v
      +----------+      +-----------+
      | ARCHIVED |      | WITHDRAWN |
      +----------+      +-----------+
```

---

## 2. State Descriptions & Transition Guardrails

### 2.1 `draft`
- Created by release manager with version, channel, and release notes.
- No artifact attached yet.
- Not visible to public or standard dashboard users.

### 2.2 `building`
- Builder compiles TypeScript, generates Vite bundle, runs secret scan, and packages ZIP.
- If an unhandled error or secret pattern is detected, transitions immediately to `failed`.

### 2.3 `ready_for_review`
- Artifact is successfully stored in object storage with sidecar `checksum.sha256`.
- Root `manifest.json` and Manifest V3 structure validated.
- Download is still blocked for standard users.

### 2.4 `approved`
- Authorized release manager verifies changelog, test execution, and security report.
- Ready for immediate or scheduled publication.

### 2.5 `published`
- Release is live.
- `published_at` timestamp recorded.
- Active pointer for the channel (`stable`, `beta`, or `internal`) is updated in PostgreSQL.
- Dashboard automatically resolves this version on next page load.
- Artifact becomes **immutable** (cannot be overwritten or re-packaged).

### 2.6 `withdrawn`
- Used in emergency scenarios (zero-day vulnerability, severe meeting capture bug).
- Downloads for this version are blocked with `HTTP 403`.
- Active pointer rolls back to the previous approved stable version.

### 2.7 `archived`
- Former stable versions when a newer version is published.
- Preserved in Version History.
- Downloadable by users needing to test or run older builds.

---

## 3. Automatic Dashboard Cache & Pointer Updates

1. **Client Page Load**: The Web Dashboard component fetches `/api/v1/extensions/releases/latest?channel=stable`.
2. **Server Resolution**: The backend queries `extension_releases` for `status = 'published'` ordered by `published_at DESC`.
3. **No Frontend Code Change**: As soon as `published` is committed in the database, every connected client receives the new version number, changelog, and verified SHA-256 checksum without redeploying the dashboard!

