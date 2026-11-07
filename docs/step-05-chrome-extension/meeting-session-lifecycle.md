# Meeting Session Lifecycle & State Machine
## Specification: Step 05 — Section 7 & Section 15

---

## 1. State Machine Definition

The extension core implements a deterministic, centralized Finite State Machine (`SessionController`). Every change in user action, tab navigation, audio track state, or WebSocket connection is governed by strict transition guards.

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> PLATFORM_DETECTED: Supported URL Detected
    PLATFORM_DETECTED --> MEETING_DETECTED: Active Meeting Signals Found
    PLATFORM_DETECTED --> IDLE: Navigation Away
    MEETING_DETECTED --> CONSENT_REQUIRED: User Opens Extension
    MEETING_DETECTED --> IDLE: Call Ended
    CONSENT_REQUIRED --> PERMISSION_REQUIRED: Consent Confirmed
    CONSENT_REQUIRED --> IDLE: Cancel / Navigation
    PERMISSION_REQUIRED --> READY: Mic & Tab Audio Ready
    PERMISSION_REQUIRED --> FAILED: Permission Denied
    READY --> STARTING: User Clicks Start Capture
    READY --> IDLE: Navigation Away
    STARTING --> CAPTURING: Stream ID Acquired & WS Connected
    STARTING --> FAILED: Capture Failed to Arm
    CAPTURING --> PAUSED: User Clicks Pause
    CAPTURING --> RECONNECTING: Network Drop / WS Error
    CAPTURING --> STOPPING: User Clicks Stop & Analyze
    CAPTURING --> FAILED: Hardware Unplugged
    PAUSED --> CAPTURING: User Clicks Resume
    PAUSED --> STOPPING: User Clicks Stop
    RECONNECTING --> CAPTURING: WS Reconnected Successfully
    RECONNECTING --> FAILED: Max Retries Exceeded
    STOPPING --> PROCESSING: Audio Tracks Stopped & Flushed
    PROCESSING --> COMPLETED: Backend Acknowledges Completion
    COMPLETED --> IDLE: Reset for Next Meeting
    FAILED --> IDLE: User Acknowledges Error
```

---

## 2. State Invariants & Invariant Guards

1. **Consent Gate:** Capture CANNOT transition from `READY` to `STARTING` without `consentConfirmed === true`.
2. **Idempotent Stop:** Invoking `STOP_CAPTURE_COMMAND` multiple times yields identical safe teardown; no double teardown crashes.
3. **Audio Suppression during Pause:** When state is `PAUSED`, the `AudioManager` immediately halts chunk dispatch. No frames or silence bytes are transmitted over WebSocket.
4. **Clean Session Teardown:** When transitioning to `STOPPING` or `COMPLETED`:
   - All `MediaStream` tracks are stopped (`track.stop()`).
   - Web Audio `AudioContext` instances are closed.
   - `AudioWorkletNode` connections are disconnected.
   - The Offscreen Document is closed via `OffscreenManager.closeOffscreenDocument()`.
   - The WebSocket sends `session_stop` and closes cleanly.

