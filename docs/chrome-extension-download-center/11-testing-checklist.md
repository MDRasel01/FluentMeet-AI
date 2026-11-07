# Testing Checklist — Chrome Extension Download Center

This checklist enumerates all test requirements defined in Section 14 of the specification.

---

## 1. Dashboard UI Testing Matrix

| Test Item | Verification Method | Expected Result | Status |
|---|---|---|---|
| **Navigation Visibility** | Inspect Web Dashboard sidebar | `Chrome Extension` nav button visible under System group | **PASS** |
| **Page Route Transition** | Click `Chrome Extension` sidebar item | Navigates to Chrome Extension page; URL/state updates | **PASS** |
| **Latest Version Display** | Check Version Badge on main card | Displays `v1.0.0 Stable` from database release record | **PASS** |
| **Release Date Display** | Check metadata row | Formatted release date displayed dynamically | **PASS** |
| **Download Button Action** | Click `Download Chrome Extension (ZIP)` | Initiates download of latest verified ZIP package | **PASS** |
| **Filename Verification** | Verify downloaded filename | Filename formatted as `fluentmeet-ai-v<version>.zip` | **PASS** |
| **File Size Display** | Check package size metric | Accurate file size displayed (e.g. `96.0 KB`) | **PASS** |
| **Checksum Display & Copy** | Click `Copy Checksum` button | Full SHA-256 copied to clipboard with green confirmation toast | **PASS** |
| **Release Notes Display** | Review What's New section | Bulleted list of features, improvements, and fixes rendered | **PASS** |
| **Version History Table** | View table rows | All published historical releases listed in reverse chronological order | **PASS** |
| **Historical Download** | Click `Download` on archived release | Initiates download of that specific historical version archive | **PASS** |
| **Draft Release Filtering** | Check public/dashboard response | Draft releases are excluded from public version history | **PASS** |
| **Withdrawn Release Guard** | Attempt download of withdrawn release | Download returns `HTTP 403 Forbidden` and is blocked | **PASS** |
| **Installation Guide** | Review 9-step instructions | Clear, responsive step-by-step unpacked guide displayed | **PASS** |
| **Web Store Callout** | Review dual-channel banner | Clear differentiation between Web Store auto-updates and ZIP | **PASS** |
| **Light & Dark Themes** | Toggle theme switch in workbench | All text, cards, borders, and buttons adapt properly | **PASS** |

---

## 2. Automated Release & Packaging Testing Matrix

| Test Item | Verification Method | Expected Result | Status |
|---|---|---|---|
| **Extension Unit Tests** | `pnpm --filter @fluentmeet/extension test` | 18 unit tests across FSM, audio, and platform detect pass | **PASS** |
| **Extension Compilation** | `pnpm --filter @fluentmeet/extension build` | Vite outputs `service-worker.js`, `sidepanel.html`, `dist/` | **PASS** |
| **Packager CLI Execution** | `python scripts/package_extension.py` | Validates dist, computes SHA-256, generates ZIP | **PASS** |
| **ZIP Root Manifest Check** | Inspect archive file tree | `manifest.json` located directly at root of ZIP | **PASS** |
| **Manifest V3 Structure** | Validate manifest JSON | `manifest_version: 3`, permissions, side panel verified | **PASS** |
| **Secret Scanning Enforcement** | Inject test `.env` file into archive | Packager halts with `Security violation` exception | **PASS** |
| **SHA-256 Integrity Verification** | Checksum calculation | Checksum matches byte-for-byte between file and database | **PASS** |
| **Sidecar Output Generation** | Inspect release directory | Generates `checksum.sha256` and `release-manifest.json` | **PASS** |
| **CI/CD Workflow Config** | Inspect `.github/workflows/extension-release.yml` | Tag-triggered automated build, test, and package pipeline | **PASS** |

---

## 3. Security & RBAC Testing Matrix

| Test Item | Verification Method | Expected Result | Status |
|---|---|---|---|
| **Admin Route Protection** | Call `/admin/extensions/releases` unauthenticated | Returns `HTTP 401` or `403` Unauthorized | **PASS** |
| **Tampered Checksum Detection** | Modify artifact bytes on disk | Retrieval catches mismatch and blocks stream with `HTTP 500` | **PASS** |
| **Download Audit Logging** | Trigger download with custom User-Agent | Record added to `extension_download_logs` with platform | **PASS** |
| **Release Event Audit Trail** | Publish release | Events logged in `extension_release_events` | **PASS** |
| **Rollback Permission** | Execute emergency rollback | Withdrawn status set and active pointer reverts to prior release | **PASS** |

---

## 4. Real Chrome Installation Testing Matrix

| Test Item | Verification Method | Expected Result | Status |
|---|---|---|---|
| **Extract Package to Folder** | Unzip `fluentmeet-ai-v1.0.0.zip` | Extracted successfully into flat directory | **PASS** |
| **Verify Unpacked Root** | Inspect extracted folder contents | `manifest.json`, `sidepanel.html`, `src/` present | **PASS** |
| **Inspect Manifest V3** | Check permissions and host permissions | Meets, Zoom, Teams, sidePanel, tabCapture present | **PASS** |
| **Offscreen Document Pipeline** | Check `pcm-processor.js` path | File present and accessible in audio worklet resources | **PASS** |
| **Side Panel Entry Point** | Check `sidepanel.html` | HTML loads compiled React bundle and styles | **PASS** |
| **Zero Sensitive Keys in Bundle** | Scan bundled JS chunks for API keys | No Gemini keys, private certs, or test secrets found | **PASS** |

---

## 5. Chrome Web Store Integration Status

| Requirement | Current Status | Notes |
|---|---|---|
| **Chrome Web Store Production Listing** | **BLOCKED (External Credential Dependency)** | Requires Google Chrome Web Store Developer Console account ($5 registration fee, developer verification, and Google OAuth client credentials). In accordance with Section 14 guidelines, this is marked **BLOCKED** rather than fabricated. |
| **Web Store Storefront Link & Guidance** | **PASS** | Deep link and auto-update architecture fully integrated into Dashboard UI. |

