# Chrome Extension High-Fidelity UI Specification

**Product Name:** AI Meeting English Coach  
**Document ID:** EXT-DESIGN-V1.0  
**Phase:** Step 02  
**Target Shell:** Chrome Side Panel API (`chrome.sidePanel`, Manifest V3)  
**Implemented Screens:** 15 / 15 Screens (100%)  
**Status:** Approved Extension UI Baseline  

---

## 1. Extension Shell & Dimensional Boundaries

The Chrome Extension operates within the browser side panel, providing a lightweight, persistent interface adjacent to Google Meet, Zoom Web, or Microsoft Teams:

- **Target Width:** 360px – 400px (fully responsive down to 320px).
- **Height:** 100% viewport height.
- **Persistent Header:** App logo, title, extension version badge (`v1.0.2`), and settings gear icon.
- **Persistent Footer:** Real-time connection status pill and sign-out link.

---

## 2. Comprehensive 15-Screen Specifications

### Screen 01 — Authentication
- **Purpose:** Onboard the user into the extension and synchronize JWT authentication tokens with the web session.
- **UI Elements:** Lock icon, welcome title, email/password form inputs, primary "Authenticate Extension" button, and link to Web Dashboard registration.

### Screen 02 — Home / Ready State
- **Purpose:** Idle state indicating extension background workers are active, waiting for the user to join a meeting.
- **UI Elements:** Pulsing radio radar icon, descriptive waiting text, supported platform URL list, and simulation trigger.

### Screen 03 — Meeting Detected
- **Purpose:** Triggered when content scripts identify active meeting DOM elements on supported URLs.
- **UI Elements:** Platform badge (`Google Meet Detected`), meeting title, discovered participant count, avatar roster preview, mandatory consent confirmation checkbox, and disabled "Start Analysis" button until consent is checked.

### Screen 04 — Participant List
- **Purpose:** Expanded roster displaying all attendees discovered by the DOM mutation observer.
- **UI Elements:** Participant names, roles (Local Speaker vs. Remote Participant), and live speaking/muted status chips.

### Screen 05 — Consent Confirmation
- **Purpose:** Educational modal/screen detailing legal two-party wiretapping requirements.
- **UI Elements:** Shield icon, regulatory explanation, and "I Understand & Agree" action button.

### Screen 06 — Live Session & Recording Dashboard
- **Purpose:** In-call operational view providing real-time audio telemetry and controls.
- **UI Elements:**
  - Red pulsing live recording dot with high-contrast monospace session timer (`14:28`).
  - Dual VU Signal Meters: Real-time animated level meters for **Your Microphone** and **Meeting Tab Audio**.
  - Control Buttons: "Pause Session" (outline) and "Stop & Analyze" (destructive red).

### Screen 07 — Paused Session
- **Purpose:** Temporary suspension of audio streaming during confidential meeting moments.
- **UI Elements:** Amber paused icon, suspended status indicator, "Resume" button, and "Stop & Process" button.

### Screen 08 — Processing & Pipeline Sync
- **Purpose:** Visual progress feedback while audio chunks are stitched, transcribed, and analyzed.
- **UI Elements:** Circular animated SVG spinner, current processing stage indicator ("Stage 2 of 3: Speaker Diarization & Gemini AI Evaluation"), and informational note explaining that the panel may safely be closed.

### Screen 09 — Completed & Report Summary
- **Purpose:** Immediate post-meeting feedback card.
- **UI Elements:** Green checkmark icon, spoken score badge (82/100, Proficient), quick metric highlights (4 grammar suggestions, 3 vocabulary upgrades, 142 WPM), and primary "View Full Report in Dashboard" CTA.

### Screen 10 — Error: Permission Denied
- **Purpose:** Surfaces when Chrome blocks microphone or tab audio access.
- **UI Elements:** Rose alert icon, step-by-step guidance to unlock permissions in the browser address bar, and "Retry Permission Check" button.

### Screen 11 — Error: Audio Capture Failure
- **Purpose:** Surfaces if tab audio capture fails to bind.
- **UI Elements:** Amber volume icon, instructions on checking "Also share tab audio", and "Re-select Tab Audio" button.

### Screen 12 — Error: Connection Lost
- **Purpose:** Active whenever the WebSocket stream disconnects.
- **UI Elements:** Offline wifi icon, reassurance that audio is safely buffering in local IndexedDB storage, countdown timer, and "Reconnect Now" button.

### Screen 13 — Error: Unsupported Platform
- **Purpose:** Triggered when the user attempts to arm recording on unsupported websites.
- **UI Elements:** Help icon, list of supported meeting domains, and return to ready button.

### Screen 14 — Error: Session Interrupted
- **Purpose:** Handles unexpected tab closures or browser crashes.
- **UI Elements:** Warning banner with action to recover and process all buffered audio captured up to the interruption point.

### Screen 15 — Extension Settings
- **Purpose:** Local extension configuration.
- **UI Elements:** Auto-detect meeting toggle, mandatory consent prompt toggle, and stereo track separation mode toggle.

