# Extension System Architecture
## Specification: Step 05 — Section 4

---

## 1. High-Level Architecture Overview

FluentMeet AI's Chrome Extension operates on a decoupled multi-context Manifest V3 architecture designed to overcome the strict limitations of Chrome service workers (no DOM access, no Web Audio API, ephemeral lifecycles) while maintaining high performance, minimal memory footprints, and security isolation.

```mermaid
flowchart TD
    subgraph BrowserContext["User Browser Context"]
        Tab["Meeting Tab\n(Google Meet / Zoom / Teams)"]
        CS["Content Script\n(Defensive DOM Metadata Observer)"]
        SP["Side Panel UI\n(React 19 + Zustand)"]
    end

    subgraph ExtensionBackground["Manifest V3 Background Context"]
        SW["Background Service Worker\n(Session Controller + Stream Id Broker)"]
        Storage["chrome.storage.session / local\n(Persistent FSM State)"]
    end

    subgraph OffscreenContext["Offscreen Document Context (USER_MEDIA)"]
        OD["Offscreen Controller"]
        TC["Pipeline A: Tab Audio Capture\n(Pass-through monitor to Destination)"]
        MC["Pipeline B: Microphone Capture\n(Echo cancellation & AGC)"]
        AW["AudioWorklet Thread\n(pcm-processor.js)"]
        AR["Resampler & Normalizer\n(16 kHz Mono S16LE)"]
        Encoder["Binary Frame Encoder\n(ArrayBuffer Packager)"]
        WSClient["WebSocket Client\n(Bounded Buffer + Backoff)"]
    end

    subgraph SaaSBackend["FastAPI SaaS Ingestion Engine"]
        API["FastAPI Meeting Lifecycle Endpoints\n(/start, /pause, /resume, /stop)"]
        WSServer["WebSocket Audio Ingestion Endpoint\n(/ws/v1/sessions/{id} & /ws/meetings/{id}/audio)"]
    end

    Tab --> CS
    CS -- "MEETING_PAGE_DETECTED\nPARTICIPANTS_UPDATED" --> SW
    SP -- "START_CAPTURE_COMMAND\nPAUSE / RESUME / STOP" --> SW
    SW <--> Storage
    SW -- "getMediaStreamId()" --> Tab
    SW -- "START_OFFSCREEN_CAPTURE\n(streamId, wsUrl, token)" --> OD
    OD --> TC
    OD --> MC
    TC --> AW
    MC --> AW
    AW --> AR
    AR --> Encoder
    Encoder --> WSClient
    WSClient <== "Binary Audio Frames (PCM S16LE)\naudio_ack Handshakes" ==> WSServer
    SP <== "REST Endpoints" ==> API
    OD -- "OFFSCREEN_AUDIO_METRICS\n(Dual VU Meters)" --> SW
    SW --> SP
```

---

## 2. Component Responsibility Matrix

| Component | Execution Context | Lifecycle | Primary Responsibilities |
|---|---|---|---|
| **Service Worker** (`service-worker.ts`) | Background Worker | Ephemeral (terminates after ~30s idle) | Extension lifecycle, action click listener, tab query & stream ID broker (`chrome.tabCapture.getMediaStreamId`), message router, offscreen lifecycle. |
| **Session Controller** (`session-controller.ts`) | Service Worker | Restores on wakeup | Manages 14-state FSM, persists session snapshot to `chrome.storage.session`, enforces valid transitions. |
| **Offscreen Document** (`offscreen.html` / `offscreen.ts`) | Hidden HTML DOM Context | Active during recording | Hosts DOM/Web Audio APIs, manages `AudioContext`, loads `AudioWorklet`, runs WebSocket streaming client. |
| **Tab Audio Capture** (`tab-audio-capture.ts`) | Offscreen Document | Active during recording | Consumes tab stream ID via `getUserMedia()`, preserves speaker playback via `sourceNode.connect(audioContext.destination)`. |
| **Microphone Capture** (`microphone-capture.ts`) | Offscreen Document | Active during recording | Captures local microphone with hardware acoustic echo cancellation and noise suppression. |
| **AudioWorklet Processor** (`pcm-processor.ts`) | Dedicated Audio Rendering Thread | Runs at AudioContext clock | Gathers 128-frame blocks, downmixes to mono, and emits raw Float32 chunks. |
| **Audio Resampler & Normalizer** (`audio-resampler.ts`) | Offscreen Document | Synchronous chunk worker | Linear interpolation downsampling to 16 kHz, Int16 S16LE conversion, RMS/Peak/Clipping metrics calculation. |
| **Binary Audio Encoder** (`audio-encoder.ts`) | Offscreen Document | Per-chunk serializer | Serializes chunk metadata and raw PCM into compact 23+N byte binary `ArrayBuffer`. |
| **Platform Adapters** (`platforms/*`) | Content Script & Service Worker | Document lifecycle | Matches URLs, queries DOM selectors defensively, monitors participant join/leave events. |
| **Side Panel UI** (`ExtensionApp.tsx`) | Chrome Side Panel | User toggled | Renders 15 reactive screens, displays real-time dual VU signal meters, triggers capture commands. |

---

## 3. End-to-End Capture Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as Meeting Participant
    participant SP as React Side Panel
    participant SW as Service Worker
    participant OD as Offscreen Document
    participant Worklet as AudioWorklet Thread
    participant WS as FastAPI Backend

    User->>SP: Opens Side Panel & Checks Consent Box
    User->>SP: Clicks "Start Analysis Session"
    SP->>SW: START_CAPTURE_COMMAND (meetingId, title, platform)
    SW->>SW: FSM Transition: READY -> STARTING
    SW->>SW: Ensure Offscreen Document (USER_MEDIA reason)
    SW->>SW: chrome.tabCapture.getMediaStreamId({targetTabId})
    SW->>OD: START_OFFSCREEN_CAPTURE (streamId, token, wsUrl)
    OD->>WS: Connect WebSocket & send session_init
    WS-->>OD: session_ready & connection_ack
    OD->>OD: Start TabAudioCapture (preserves speaker playback)
    OD->>OD: Start MicrophoneCapture (isolated)
    OD->>Worklet: Audio Frames into Worklet
    Worklet-->>OD: Float32 Mono Chunks
    OD->>OD: Resample to 16kHz + Convert to S16LE
    OD->>OD: Encode Binary Frame (version, seq, ts, pcm)
    OD->>WS: sendBinaryFrame(ArrayBuffer)
    WS-->>OD: audio_ack (sourceId, seq, sampleCount)
    OD->>SW: OFFSCREEN_AUDIO_METRICS (micVolume, tabVolume)
    SW->>SP: Update Dual VU Meters in Live Session UI
```

---

## 4. Service Worker Sleep Recovery Guarantee

Chrome terminates Manifest V3 Service Workers after roughly 30 seconds of inactivity. To prevent state loss:
1. `SessionController` immediately synchronizes every state transition and active metadata update to `chrome.storage.session` (in-memory persistent storage for the browser session).
2. On any incoming message or wakeup event, `sessionController.restoreState()` immediately hydrates the active session snapshot.
3. The actual long-running media streams and WebSocket connection reside within the **Offscreen Document**, which Chrome does not terminate while audio capture nodes remain active.
4. If the browser or extension restarts, the state machine restores to `IDLE` or prompts the user with the action state, preventing orphaned sessions.

