# Versioning & Compatibility Policy

## 1. Semantic Versioning (SemVer)

All FluentMeet AI Chrome Extension releases strictly follow **Semantic Versioning 2.0.0**:

$$\text{Format: } \text{MAJOR}.\text{MINOR}.\text{PATCH}$$

- **`MAJOR` (e.g. `2.0.0`)**: Incompatible API changes, major architectural redesign, or breaking changes to the WebSocket streaming protocol.
- **`MINOR` (e.g. `1.1.0`)**: Backwards-compatible new functionality (e.g. adding MS Teams Web support, new speech metric overlays).
- **`PATCH` (e.g. `1.0.1`)**: Backwards-compatible bug fixes, performance improvements, and security patches.

---

## 2. Manifest Synchronization

The extension's `manifest.json` version string must **always** match the release database record:
- If `manifest.json` specifies `"version": "1.0.0"`, the database record must be `1.0.0`.
- The packaging script automatically updates `manifest.json` inside the generated ZIP archive if a version override is specified.

---

## 3. Platform & Browser Compatibility Matrix

| Component | Minimum Supported Version | Recommended | Notes |
|---|---|---|---|
| **Google Chrome** | `116.0.0.0` | `120.0+` | Required for Manifest V3 Side Panel API & Offscreen Audio Worklet |
| **Manifest Version** | `3` | `3` | Manifest V2 is fully deprecated by Google Chrome |
| **Backend REST API** | `v1` | `v1` | Supported endpoints under `/api/v1` |
| **WebSocket Protocol** | `v1` (`/ws/audio`) | `v1` | 16kHz linear PCM 16-bit mono chunks |
| **Google Meet** | Web Client | Latest | Supported via MutationObserver |
| **Zoom Client** | Web Client (`zoom.us/wc`) | Latest | Supported via Tab Audio capture |
| **Microsoft Teams** | Teams Web App | Latest | Supported via Tab Audio capture |

---

## 4. Breaking Change Protocol

When a breaking backend API change occurs:
1. Backend maintains backwards compatibility on `/api/v1` for at least 60 days.
2. Older extension versions send an `X-Client-Version` header; if incompatible, backend responds with `426 Upgrade Required` containing the latest Dashboard download URL.
3. The Web Dashboard displays an upgrade notification banner to prompt the user to update their unpacked extension or pull from the Chrome Web Store.

