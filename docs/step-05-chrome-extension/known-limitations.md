# Documented Platform Constraints & Known Limitations
## Specification: Step 05 — Section 22.24 & Section 25.G

---

## 1. Architectural Boundaries & Platform Scope

1. **Web-Based Meeting Clients Only:**
   - The Chrome extension operates exclusively within Chromium browser tabs.
   - It captures **Google Meet Web** (`meet.google.com`), **Zoom Web Client** (`*.zoom.us/wc/*`), and **Microsoft Teams Web** (`teams.microsoft.com`).
   - Native desktop executable clients (e.g., Zoom.exe, Teams native Electron app) cannot be captured directly via Chrome extension APIs. Users must open the meeting via their web browser.
2. **Tab Capture Muting Override:**
   - Chrome's underlying `tabCapture` engine automatically diverts the audio output stream away from physical speakers. FluentMeet AI restores this using a pass-through connection to `AudioContext.destination`. In rare cases where an enterprise group policy strictly restricts Web Audio destination routing, users must use headphones.
3. **Multi-Speaker Diarization Boundary:**
   - The extension collects separate audio for the local user (`sourceId: 1`) and the combined remote meeting audio (`sourceId: 0`), along with participant names discovered in the DOM.
   - Diarization (who spoke when among remote attendees) is calculated exclusively on the SaaS backend in Step 06 to ensure accuracy and low client CPU consumption.
4. **Cross-Browser Compatibility:**
   - Safari and Firefox do not implement the `chrome.tabCapture.getMediaStreamId()` or `chrome.offscreen` APIs. Chromium-based browsers (Chrome, Edge, Brave) running version 116+ are required.

