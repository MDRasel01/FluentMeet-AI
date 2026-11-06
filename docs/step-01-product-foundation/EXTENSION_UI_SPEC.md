# Chrome Extension UI/UX Specification (Manifest V3)

**Product Name:** AI Meeting English Coach  
**Document ID:** SPEC-EXT-V1.0  
**Status:** Approved Extension UI Specification  
**Version:** 1.0.0  

---

## 1. Extension Architecture & Side Panel Constraints

The Chrome Extension operates within the Chrome Side Panel API (`chrome.sidePanel`), providing an ambient, persistent sidebar interface without obstructing meeting video tiles or shared screens.

- **Width:** Dynamically resized by the user (Minimum: 320px, Default: 380px).
- **Height:** 100% of the active browser viewport height.
- **Context Separation:**
  - `sidepanel.tsx`: Pure React UI running in the side panel window.
  - `offscreen.ts`: Headless document executing Web Audio API and `MediaStreamTrack` chunking.
  - `service_worker.ts`: Background coordinator managing authentication tokens, tab state, and WebSockets.
  - `content_script.ts`: Injected DOM observers on `meet.google.com`, `zoom.us`, and `teams.microsoft.com`.

---

## 2. Seven Core Extension Screens

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Screen 01: Auth  │ ──► │ Screen 02: Ready │ ──► │ Screen 03: Detect│
└──────────────────┘     └──────────────────┘     └────────┬─────────┘
                                                           │ User Consents & Starts
                                                           ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Screen 06: Done  │ ◄── │ Screen 05: Proc  │ ◄── │ Screen 04: Live  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
         ▲                        ▲                        ▲
         └────────────────────────┴────────────────────────┘
                                  │ Error Occurs
                                  ▼
                         ┌──────────────────┐
                         │ Screen 07: Error │
                         └──────────────────┘
```

---

### Screen 01 — Authentication
- **Purpose:** Onboard or authenticate the user into the extension and sync JWT session credentials.
- **UI Layout:**
  - Header: Logo + Title (`"AI Meeting English Coach"`).
  - Body:
    - If user is logged into Web Dashboard in another tab: `"Detected web session as {user.email}". [Connect Account]` button.
    - If not logged in: Email Input, Password Input, Primary `"Log In"` Button, `"Forgot Password?"` link.
    - Secondary Link: `"Don't have an account? Sign up on Web"`.
- **States:** Default, Authenticating (Spinner on button), Error (Invalid credentials banner).

---

### Screen 02 — Home / Ready State
- **Purpose:** Idle state indicating extension is healthy, waiting for the user to navigate to an online meeting.
- **UI Layout:**
  - Header: User Profile Pill (Avatar + Name) + Settings Gear Icon.
  - Status Card:
    - Status Indicator: Gray pulsing dot (`"Idle — Waiting for meeting"`).
    - Supported platforms graphic: Google Meet, Zoom Web, Microsoft Teams.
  - Quick Info Box:
    - Tips on how to start: *"Navigate to meet.google.com and join a call. Analysis will arm automatically."*
  - Footer Action: `"Open Web Dashboard"` button.

---

### Screen 03 — Meeting Detected & Consent Confirmation
- **Purpose:** Triggered when the content script discovers an active meeting URL and DOM. Displays meeting metadata and collects mandatory consent.
- **UI Layout:**
  - Header: Platform Badge (`Google Meet`), Meeting Title (e.g., `"Sprint Planning Call"`).
  - Detected Participants Panel:
    - Participant Count Badge (`4 Participants Detected`).
    - Discovered Avatar Stack & Names: Scraped dynamically from the DOM.
  - **Mandatory Consent Checkbox (Enforced):**
    - `[ ] "I confirm that all call participants are aware and have consented to AI audio analysis."`
  - Action Controls:
    - Primary Button: `"Start Analysis"` (Disabled until consent checkbox is checked).
    - Secondary Button: `"Dismiss for this Call"`.

---

### Screen 04 — Live Session & Recording Controls
- **Purpose:** Active in-call dashboard providing real-time audio health feedback and session controls.
- **UI Layout:**
  - Recording Status Bar:
    - Red pulsing recording dot + Elapsed Duration Timer (`14:28`).
  - Dual Audio VU Meters:
    - **Your Microphone:** Real-time green animated decibel level meter.
    - **Meeting Tab Audio:** Real-time green decibel level meter.
  - Active Speaker Indicator: Shows currently speaking participant name with voice animation.
  - Session Controls (Bottom Fixed Bar):
    - `[Pause / Resume]` Toggle Button (Amber).
    - `[Stop & Analyze]` Primary Button (Solid Red).

---

### Screen 05 — Processing & Uploading
- **Purpose:** Communicates post-meeting data synchronization, chunk finalization, and AI pipeline progress.
- **UI Layout:**
  - Progress Animation: Circular animated SVG progress ring.
  - Status Message: `"Finalizing audio upload..."` $\to$ `"Processing ASR & Diarization..."` $\to$ `"Generating Gemini English Report..."`.
  - Estimated Time Indicator: e.g., *"Typically takes ~60 seconds"*.
  - Action: `"You can close this panel. We'll notify you on the dashboard when ready."` Button: `"Open Dashboard"`.

---

### Screen 06 — Session Completed & Report Ready
- **Purpose:** Immediate post-meeting feedback card linking to the full web report.
- **UI Layout:**
  - Success Icon (Green Checkmark).
  - Meeting Summary Card:
    - Meeting Duration: `32 mins` | Words Spoken: `1,420 words`.
    - Spoken English Score: `82 / 100` (Proficient).
    - Quick Insights: e.g., *"3 grammar suggestions, 4 vocabulary upgrades ready."*
  - Primary Action Button: `"View Full Report in Dashboard"` (Opens new tab to `/meetings/[id]/report/me`).
  - Secondary Action: `"Back to Ready"`.

---

### Screen 07 — Error State & Recovery Matrix
- **Purpose:** Actionable error guidance whenever hardware, network, or third-party DOM issues occur.
- **UI Layout:**
  - High-visibility Error Icon (Amber triangle or Red circle).
  - Clear Error Title (e.g., *"Microphone Permission Blocked"*).
  - Explanatory Description with immediate resolution steps.
  - Primary CTA: `"Retry Permission"` or `"Reconnect WebSocket"`.

#### Common Recovery Scenarios

| Error Condition | Displayed Message | User Recovery Action |
|---|---|---|
| **Mic Permission Denied** | *"Chrome cannot access your microphone."* | Click "Open Settings", toggle microphone permissions to Allow, and click "Retry". |
| **Tab Audio Not Shared** | *"Meeting tab audio was not selected."* | Click "Select Tab Audio" and ensure "Also share tab audio" checkbox is checked. |
| **WebSocket Dropped** | *"Connection lost. Buffering locally..."* | Auto-reconnects with countdown; manual "Reconnect Now" button provided. |
| **DOM Selector Drift** | *"Unable to detect participant names."* | Session continues as generic "Speaker 1, Speaker 2" with user notification. |

---

## 3. Session Continuity & Lifecycle Rules

1. **Side Panel Closing Immunity:**
   The audio capture stream, WebSockets, and chunk buffers are managed in the background `service_worker.ts` and `offscreen.ts`. If the user accidentally closes the Chrome Side Panel during a meeting, **recording does not terminate**. Re-opening the side panel immediately re-binds to the active background session.
2. **Tab Refresh / Navigation Warning:**
   If the user navigates away from the meeting tab while recording is active, a browser `beforeunload` warning is triggered to prevent accidental session loss.

