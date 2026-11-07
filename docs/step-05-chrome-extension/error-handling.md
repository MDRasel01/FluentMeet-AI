# Error Handling Matrix & Recovery Procedures
## Specification: Step 05 — Section 18

---

## 1. Error Codes & Recovery Matrix

| Error Code | Trigger Condition | UI Recovery Screen | Recovery Action |
|---|---|---|---|
| `AUTH_REQUIRED` | Missing or cleared authentication token. | `auth` | Prompts user to authenticate with email & password. |
| `AUTH_EXPIRED` | Expired JWT token during meeting check. | `auth` | Attempts token refresh; on failure, prompts re-login. |
| `PLATFORM_UNSUPPORTED` | Active browser tab is not Google Meet, Zoom, or Teams. | `error-unsupported` | Informs user of supported meeting URLs with quick link. |
| `MEETING_NOT_ACTIVE` | User opened extension on meeting lobby page before joining. | `home` | Remains in passive listening mode until meeting is joined. |
| `CONSENT_REQUIRED` | User attempted capture without checking consent mandate. | `detected` | Disables Start button; prompts consent check. |
| `TAB_CAPTURE_DENIED` | User denied tab capture or browser blocked stream ID. | `error-audio` | Explains how to select meeting tab and verify checkbox. |
| `MICROPHONE_PERMISSION_DENIED` | Browser microphone permission was blocked. | `error-permission` | Instructs user to click browser URL lock icon and allow microphone. |
| `MICROPHONE_UNAVAILABLE` | Physical microphone device was unplugged or occupied. | `error-permission` | Prompts reconnecting audio input device. |
| `WEBSOCKET_CONNECT_FAILED` | Inability to establish initial socket connection. | `error-connection` | Displays retry button and exponential backoff status. |
| `WEBSOCKET_DISCONNECTED` | Socket dropped during live session. | `live` (status badge: Reconnecting) | Buffers audio in bounded queue while auto-reconnecting. |
| `SESSION_INTERRUPTED` | Meeting tab was closed prematurely while recording. | `error-interrupted` | Offers user option to process captured audio up to drop point. |

