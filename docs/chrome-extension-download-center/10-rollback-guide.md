# Rollback & Emergency Procedures

## 1. Emergency Scenarios

An emergency rollback or withdrawal is triggered under any of the following conditions:
- Critical regression in Tab Audio Capture or WebSocket streaming.
- Unhandled service worker crashes on meeting detection.
- Security vulnerability discovered in a client dependency.
- Incompatible changes affecting meeting platform DOM parsing.

---

## 2. Server-Side Rollback Workflow

```
Administrator Detects Critical Defect
                 |
                 v
Admin Console: Extension Releases
                 |
                 v
Select Faulty Release -> Click [Rollback]
                 |
                 v
POST /api/v1/admin/extensions/releases/{id}/rollback
                 |
                 v
Database Actions:
- Faulty release marked: 'withdrawn'
- Download attempts blocked (HTTP 403)
- Latest pointer reverts to prior approved 'published' release
                 |
                 v
Dashboard Updates Instantly:
- Latest download button now serves prior stable version
- Audit event logged in extension_release_events
```

---

## 3. Important Architectural Realities

### Reality 1: Dashboard Rollback vs Installed Extension State
> **CRITICAL:** Rolling back the download pointer on the Web Dashboard **does not automatically downgrade extensions already installed in users' browsers**.  
> The Chrome extension runtime has no native API permitting an external server to force a downgrade to a lower SemVer number.

### Reality 2: Remediation Strategy for Installed Users

1. **For Chrome Web Store Users**:
   - Chrome does not permit submitting a lower version number.
   - To fix an issue in production `v1.0.1`, the team must publish an emergency hotfix with a higher version number: **`v1.0.2`**.
   - Chrome will detect `v1.0.2` as higher than `v1.0.1` and automatically push it to all users.

2. **For Unpacked Dashboard ZIP Users**:
   - Release administrators withdraw `v1.0.1` on the Dashboard.
   - The Dashboard alerts users to download the rollback package (or hotfix `v1.0.2`).
   - Users replace their extracted directory and click Reload (↻) in `chrome://extensions`.

3. **Backend Safeguard (Server-Side Kill Switch)**:
   - The backend API can enforce minimum client version checks on `/ws/audio` and `/api/v1/audio/upload`.
   - If a known compromised version connects, the backend gracefully rejects the connection with:
     ```json
     {
       "error": "CLIENT_DEPRECATED",
       "message": "This extension version has been withdrawn due to a critical update. Please re-download the latest version from the dashboard."
     }
     ```

