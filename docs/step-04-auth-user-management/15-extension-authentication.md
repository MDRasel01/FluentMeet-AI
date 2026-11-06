# Chrome Extension Authentication Architecture

## 1. Extension Security Model
Browser extensions run across separated execution contexts:
- **Background Service Worker:** Trusted context; manages token lifecycles and communications with backend APIs.
- **Sidepanel UI:** Trusted context; renders user interface and coach feedback.
- **Content Scripts:** Untrusted context injected into third-party web meeting DOMs (Google Meet, Zoom, Teams). **Never receives or stores authentication tokens.**

## 2. Authentication Adapter
The extension utilizes `ExtensionAuthAdapter` (`apps/extension/src/utils/auth-adapter.ts`):
- Uses `chrome.storage.session` (memory-only in Manifest V3) to store access and refresh tokens.
- Content scripts communicate with the background worker via `chrome.runtime.sendMessage` using validated message schemas (`CHECK_MEETING_STATUS`, `MEETING_PAGE_DETECTED`).
- Session expiration automatically prompts the sidepanel UI to display the Sign In screen without disrupting the active meeting tab.
