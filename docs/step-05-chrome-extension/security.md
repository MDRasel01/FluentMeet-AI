# Security & Enterprise Privacy Standards
## Specification: Step 05 — Section 16

---

## 1. Security Model & Architecture

FluentMeet AI treats the browser extension as an untrusted public client in an enterprise environment:
1. **Isolated Context Boundaries:**
   - Content scripts injected into meeting tabs have ZERO access to authentication tokens or raw Web Audio APIs.
   - Authentication tokens reside strictly within `chrome.storage.session` (memory-preferred) or `chrome.storage.local`.
   - Communication between Content Script and Service Worker is strictly validated using Zod schemas (`message.schemas.ts`).
2. **Transport Layer Security:**
   - All REST communication is encrypted via **HTTPS**.
   - All real-time streaming is encrypted via **WSS (WebSocket Secure)** with short-lived tokens.
3. **No Embedded Long-Lived Secrets:**
   - No API keys, database credentials, or signing secrets are packaged in the extension build artifacts.
   - Source code is assumed to be publicly inspectable by end-users.

---

## 2. Multi-Tenant Isolation & Authorization

Every API request and WebSocket connection is verified by the FastAPI backend:
1. The user's JWT bearer token is decoded.
2. The `user_id` and `organization_id` claims are checked against the requested `meeting_id`.
3. If a user attempts to stream audio or access meetings belonging to another tenant or organization, the backend immediately rejects the connection with HTTP 403 or WebSocket code `1008 Policy Violation`.

---

## 3. Data Protection & Privacy Compliance

- **No Secret Audio Logging:** Raw audio samples and base64 strings are strictly excluded from console logs, telemetry events, and Sentry reports.
- **Immediate Resource Release:** Upon clicking "Stop & Analyze" or navigating away, all audio capture tracks and buffers are stopped and garbage collected.
- **Ephemeral Retention:** Audio buffered in memory during network reconnects is strictly bounded (max 100 frames) and purged on disconnect.

