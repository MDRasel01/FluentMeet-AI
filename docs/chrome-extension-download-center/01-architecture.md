# Architecture Overview — Chrome Extension Distribution & Release System

## 1. System Topology & Dual Distribution Model

The FluentMeet AI Chrome Extension distribution infrastructure operates under a strictly bifurcated distribution architecture:

```
+----------------------------------------------------------------------------------+
|                               RELEASE SOURCE REPO                                |
|             apps/extension/ (Manifest V3, React 19, Offscreen Document)          |
+----------------------------------------------------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
     [Channel A: Production Users]                 [Channel B: Dashboard & Devs]
   +-------------------------------+             +-------------------------------+
   |      Chrome Web Store         |             |   Dashboard Download Center   |
   | - Managed by Google           |             | - Managed by FluentMeet SaaS  |
   | - Background Silent Updates   |             | - Clean ZIP Source Archive    |
   | - Signed CRX Package          |             | - Unpacked Dev Mode Testing   |
   | - End-User Auto Updates       |             | - Historical Version Archive  |
   +-------------------------------+             +-------------------------------+
                 |                                             |
                 v                                             v
   Auto-Updated Chrome Browser                   Manual Unpacked Load (chrome://)
```

### Architectural Distinction: Chrome Web Store vs Dashboard Download

1. **Production Channel (Chrome Web Store)**:
   - Primary distribution channel for non-technical workplace end-users.
   - Leverages Google Chrome's built-in Omaha update protocol.
   - When Google approves a new store build, Chrome automatically updates installed extensions in the background.
   - Web Store private keys (`.pem`) are held securely in cloud HSM / secrets managers and never exposed to the monorepo, web dashboard, or client code.

2. **Manual & Archive Channel (Dashboard ZIP Download Center)**:
   - Built directly into the authenticated Web Dashboard (`/chrome-extension`).
   - Serves verified `.zip` archives where `manifest.json` sits directly at the root.
   - Intended for internal testers, developers, staging QA, enterprise policy deployments, and rolling back to historical builds.
   - Requires developer mode unpacked loading (`chrome://extensions` → *Load unpacked*).

---

## 2. Component Architecture

```
+---------------------------------------------------------------------------------------+
| WEB DASHBOARD (Next.js / Vite React App)                                              |
| - Navigation: Workspace, My English, Learning, Organization, System                   |
| - Dedicated Screen: ChromeExtensionPage.tsx                                          |
| - Dynamically queries /api/v1/extensions/releases/latest                              |
+---------------------------------------------------------------------------------------+
        |                                       ^
        | (Download ZIP request)                | (JSON Release Metadata)
        v                                       |
+---------------------------------------------------------------------------------------+
| FASTAPI BACKEND SERVICES (services/api/)                                              |
| - Router: /api/v1/extensions (User endpoints)                                         |
| - Router: /api/v1/admin/extensions (Admin endpoints)                                 |
| - Repository: ExtensionReleaseRepository                                              |
| - Storage Service: ExtensionStorageService                                            |
| - Builder Service: ExtensionBuilderService                                            |
+---------------------------------------------------------------------------------------+
        |                                       |
        v                                       v
+-------------------------------+       +-----------------------------------------------+
| POSTGRESQL DATABASE           |       | PRIVATE OBJECT STORAGE                        |
| - extension_releases          |       | storage/releases/                             |
| - extension_download_logs     |       |   └── stable/                                 |
| - extension_release_events    |       |         └── 1.0.0/                            |
+-------------------------------+       |               ├── fluentmeet-ai-v1.0.0.zip    |
                                        |               ├── checksum.sha256             |
                                        |               └── release-manifest.json       |
                                        +-----------------------------------------------+
```

---

## 3. Data Flow: New Release Publishing to Live Dashboard Update

1. **Commit & Build**: Developers commit extension updates; CI/CD or admin triggers `pnpm build` in `apps/extension`.
2. **Packaging & Security Scan**: `scripts/package_extension.py` runs secret scanning, verifies root `manifest.json`, and computes SHA-256 hash.
3. **Draft Release**: Administrator calls `POST /admin/extensions/releases` with version, channel, and release notes.
4. **Validation**: Automated checks verify Manifest V3 structure and checksum consistency.
5. **Approval & Publication**: Admin approves and publishes release; `status` transitions to `published` and `published_at` timestamp is set.
6. **Dynamic Cache Resolution**: When any user loads the Web Dashboard, `/api/v1/extensions/releases/latest` resolves the newly published record from PostgreSQL.
7. **Immediate Download Availability**: The main download button instantly resolves the new ZIP artifact with valid headers and SHA-256 verification.

