# Manifest V3 Permissions & Security Audit
## Specification: Step 05 — Section 5 & 5.1

---

## 1. Permission Matrix

The FluentMeet AI extension enforces the **Principle of Least Privilege**. Only APIs directly required for meeting detection, user-initiated tab audio capture, and offscreen processing are requested.

| Permission Name | Required / Optional | Technical Purpose | User-Facing Explanation | Security & Privacy Impact | Test Verification Case |
|---|---|---|---|---|---|
| `tabCapture` | **Required** | Generates a temporary `MediaStreamId` using `chrome.tabCapture.getMediaStreamId()` targeting the active meeting tab. | Enables capturing audio from your virtual meeting tab. | Narrowly scoped to stream ID generation; requires explicit user gesture. Does not capture unrelated tabs. | Verified in `service-worker.ts` capture sequence. |
| `offscreen` | **Required** | Creates a sandboxed offscreen HTML document with reason `USER_MEDIA` to host Web Audio and AudioWorklet nodes. | Allows the coach to process audio in the background without slowing down your browser. | Offscreen context is isolated from external scripts. Created strictly when recording starts; destroyed on stop. | Verified in `offscreen-manager.ts` lifecycle tests. |
| `sidePanel` | **Required** | Configures `chrome.sidePanel.setPanelBehavior` to open the extension interface in the Chrome side panel. | Keeps the AI coach docked beside your meeting without covering your video call. | Purely UI presentation API. Cannot inject scripts or modify web page contents. | Verified in `service-worker.ts` on installation. |
| `storage` | **Required** | Persists session FSM state and authentication tokens via `chrome.storage.session` and `chrome.storage.local`. | Saves your active session state so you don't lose progress if the extension refreshes. | Uses memory-preferred session storage; tokens are cleared immediately upon sign out. | Verified in `auth-adapter.ts` and `session-controller.ts`. |
| `activeTab` | **Required** | Grants temporary, user-initiated access to the currently focused meeting tab upon clicking the extension icon. | Allows FluentMeet to see which meeting you are on when you click the coach. | Safe permission granted only on user action. Does not grant background surveillance. | Verified during manual extension toolbar click. |
| `scripting` | **Required** | Injects the defensive meeting observer into supported meeting tabs when auto-opened. | Detects when your meeting starts or ends automatically. | Restricted strictly to declared host permissions; cannot run on arbitrary websites. | Verified in `content-script.ts` registration. |

---

## 2. Host Permissions Audit

Host permissions are strictly limited to the official meeting web client origins and the local/production backend:

```json
"host_permissions": [
  "https://meet.google.com/*",
  "https://*.zoom.us/*",
  "https://teams.microsoft.com/*",
  "http://localhost:8000/*",
  "ws://localhost:8000/*"
]
```

### Prohibited / Rejected Permissions
The following broad or sensitive permissions were reviewed and **explicitly rejected** to uphold enterprise compliance:
- ❌ `cookies`: Not required. Authentication uses bearer tokens stored in extension session storage.
- ❌ `webRequest` / `webRequestBlocking`: Bypassed; telemetry relies on standard DOM events and WebSocket.
- ❌ `debugger`: Prohibited; intrusive and violates enterprise security policies.
- ❌ `downloads`: Not needed; reports are viewed directly in the web dashboard.
- ❌ `camera`: **Never requested.** The extension captures audio exclusively.
- ❌ `<all_urls>`: Prohibited; host permissions are rigidly restricted to supported meeting platforms.

