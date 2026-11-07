# Step 05 — Chrome Extension Development
## AI Meeting English Coach SaaS

[![Manifest V3](https://img.shields.io/badge/Manifest_V3-Production_Ready-emerald.svg)](#)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-blue.svg)](https://www.typescriptlang.org/)
[![Vitest](https://img.shields.io/badge/Vitest-18_Passed-success.svg)](https://vitest.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI_Backend-16_Passed-success.svg)](https://fastapi.tiangolo.com/)

---

## 1. Executive Summary

**Step 05** delivers the enterprise-grade Chrome Manifest V3 Extension for the **FluentMeet AI** platform. The extension serves as the real-time audio capture, session orchestration, and platform telemetry client that interfaces directly with browser-based virtual meetings (Google Meet, Zoom Web, Microsoft Teams Web) and streams dual-channel audio to the FastAPI SaaS ingestion pipeline.

### Core Architectural Responsibilities
1. **Isolated Dual Capture Engine:**
   - **Pipeline A (Remote Tab Audio):** Captured via `chrome.tabCapture.getMediaStreamId()` and consumed in an isolated Offscreen Document via `navigator.mediaDevices.getUserMedia()`. Includes an active pass-through monitor node (`sourceNode.connect(audioContext.destination)`) preserving local tab audio playback without feedback loops.
   - **Pipeline B (Local Microphone):** Captured via audio-only `navigator.mediaDevices.getUserMedia()` with echo cancellation, noise suppression, and auto gain control. Disconnected from local speakers to eliminate ear feedback.
2. **AudioWorklet & Signal Normalization:**
   - Real-time downmixing to 1-channel mono.
   - Linear interpolation resampling from native hardware rates (48 kHz / 44.1 kHz) to standardized **16 kHz**.
   - Conversion to Signed 16-bit Little-Endian PCM (`Int16Array`, `S16LE`).
   - Signal dynamics metrics (RMS, peak volume, silence, clipping) computed for real-time dual VU signal meters.
3. **Binary Audio Transport:**
   - Transmits packed binary frames (`ArrayBuffer`) directly over WebSocket (`/ws/meetings/{meeting_id}/audio` or `/ws/v1/sessions/{session_id}`), avoiding base64 JSON payload overhead.
   - Monotonic session-relative timestamps (`performance.now()`) and strictly sequential chunk sequence IDs.
   - Jittered exponential backoff auto-reconnection and a bounded buffer memory queue (100 frames max).
4. **Three Platform Adapters:**
   - Dedicated adapters for Google Meet, Zoom Web Client, and Microsoft Teams Web.
   - Defensive metadata extraction (participant names, local speaker identification, call state).
   - Strict ethical boundaries: No speculative speaker diarization; unknown identities remain flagged as `unknown` for server-side evaluation.
5. **Session FSM & Two-Party Consent:**
   - 14-state deterministic Finite State Machine (`IDLE` to `COMPLETED`).
   - Persistent session storage (`chrome.storage.session` / `local`) recovering state across Service Worker terminations.
   - Mandatory user consent confirmation prior to capture arming.

---

## 2. Directory Structure

```text
apps/extension/
├── manifest.json                        # Manifest V3 configuration
├── package.json                         # Extension scripts & dependencies
├── tsconfig.json                        # Strict TypeScript compiler options
├── vite.config.ts                       # Multi-entry Rollup configuration (Sidepanel, SW, Offscreen, Worklet, Content)
├── vitest.config.ts                     # Vitest JSDOM unit test harness
├── sidepanel.html                       # Sidepanel DOM entry point
├── ExtensionApp.tsx                     # 15 React Sidepanel screens
├── src/
│   ├── background/
│   │   ├── service-worker.ts            # Extension lifecycle & tab stream orchestrator
│   │   ├── session-controller.ts        # Centralized FSM state machine & storage persistence
│   │   └── offscreen-manager.ts         # Offscreen document singleton controller
│   ├── offscreen/
│   │   ├── offscreen.html               # Offscreen DOM container
│   │   ├── offscreen.ts                 # Offscreen message dispatcher & stream supervisor
│   │   ├── audio-manager.ts             # Capture coordinator & metrics reporter
│   │   ├── tab-audio-capture.ts         # Remote tab capture (Pipeline A) & playback preservation
│   │   ├── microphone-capture.ts        # Local microphone capture (Pipeline B)
│   │   ├── audio-resampler.ts           # 16kHz resampler & S16LE PCM converter
│   │   └── audio-worklet/
│   │       └── pcm-processor.ts         # AudioWorkletProcessor thread buffer
│   ├── platforms/
│   │   ├── platform-interface.ts        # Platform adapter contract
│   │   ├── platform-detector.ts         # Unified URL matcher & adapter registry
│   │   ├── google-meet/                 # Google Meet DOM adapter
│   │   ├── zoom/                        # Zoom Web client adapter
│   │   └── microsoft-teams/             # MS Teams Web adapter
│   ├── services/
│   │   └── websocket.service.ts         # Binary WebSocket client & bounded buffer
│   ├── sidepanel/
│   │   ├── index.tsx                    # React mounting root
│   │   ├── sidepanel.css                # Tailwind base & animations
│   │   └── store/
│   │       └── extension-store.ts       # Zustand reactive extension store
│   ├── types/
│   │   ├── audio.types.ts               # Sample rates, sources, metrics
│   │   ├── extension.types.ts           # Session FSM & participant metadata
│   │   ├── platform.types.ts            # Adapter contracts
│   │   └── websocket.types.ts           # Framing protocol & event types
│   ├── schemas/
│   │   └── message.schemas.ts           # Zod validation schemas
│   └── utils/
│       ├── audio-encoder.ts             # Binary frame packing & unpacking
│       ├── auth-adapter.ts              # chrome.storage token manager
│       └── monotonic-clock.ts           # Skew-free session timer
└── tests/
    └── unit/
        ├── audio-encoder.test.ts        # Binary frame packing tests
        ├── audio-resampler.test.ts      # 16kHz resampling & PCM tests
        ├── session-state-machine.test.ts# FSM transitions & recovery tests
        ├── platform-detection.test.ts   # URL matching & defensive parsing tests
        ├── websocket-service.test.ts    # Reconnection & bounded buffer tests
        └── extension-app.test.tsx       # Sidepanel UI & consent tests
```

---

## 3. Quick Start & Verification

### Running Automated Extension Tests
```bash
cd apps/extension
pnpm test
```
*Result: 6 test suites, 18 tests passing (100%).*

### Building Extension for Production
```bash
cd apps/extension
pnpm build
```
*Output: `apps/extension/dist/` contains valid MV3 bundle with manifest, background service worker, side panel, offscreen document, AudioWorklet processor, and content script.*

### Loading into Google Chrome
1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** (toggle in upper right).
3. Click **Load unpacked** and select `h:\Rasel\all_local_Projecrt\FluentMeet-AI\apps\extension\dist`.
4. Open the Extension Side Panel or pin the FluentMeet AI icon.

