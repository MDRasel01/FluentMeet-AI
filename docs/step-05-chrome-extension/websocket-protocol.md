# WebSocket Streaming & Binary Framing Protocol
## Specification: Step 05 — Section 12

---

## 1. Binary Framing Specification

To avoid the 33% bandwidth inflation and CPU serialization overhead of JSON Base64 strings, all raw audio chunks are packed into a compact binary format (`AudioFrameEncoder`):

```text
+-------------------+--------------------+------------------------+--------------------------+
| Protocol Version  | Source Identifier  | Sequence Number        | Session Timestamp (ms)   |
| 1 Byte (Uint8)    | 1 Byte (Uint8)     | 4 Bytes (Uint32 BE)    | 8 Bytes (Float64 BE)     |
+-------------------+--------------------+------------------------+--------------------------+
| Sample Rate (Hz)  | Channel Count      | Audio Encoding         | Sample Count             |
| 2 Bytes (Uint16)  | 1 Byte (Uint8)     | 1 Byte (Uint8: 1=S16LE)| 4 Bytes (Uint32 BE)      |
+-------------------+--------------------+------------------------+--------------------------+
| Meeting ID Length | Meeting ID String  | Raw S16LE PCM Audio Payload                       |
| 1 Byte (Uint8: N) | N Bytes (UTF-8)    | (Sample Count * Channels * 2) Bytes               |
+-------------------+--------------------+------------------------+--------------------------+
```

### Field Definitions
- **Protocol Version (Offset 0):** `0x01` (Current version).
- **Source Identifier (Offset 1):**
  - `0x00`: `REMOTE_TAB` (Meeting participants).
  - `0x01`: `LOCAL_MIC` (Local speaker).
- **Sequence Number (Offset 2..5):** 32-bit unsigned integer, monotonically incrementing per source.
- **Timestamp (Offset 6..13):** 64-bit IEEE 754 floating point number representing milliseconds elapsed since session start.
- **Sample Rate (Offset 14..15):** `16000` (`0x3E80`).
- **Channel Count (Offset 16):** `1` (Mono).
- **Audio Encoding (Offset 17):** `1` (`PCM_S16LE`).
- **Sample Count (Offset 18..21):** Number of 16-bit audio samples in payload.
- **Meeting ID Length (Offset 22):** Byte length $N$ of meeting ID string.
- **Meeting ID (Offset 23..23+N-1):** Canonical string identifier.
- **PCM Audio Payload (Offset 23+N..End):** Raw signed 16-bit little-endian binary bytes.

---

## 2. Text Control Messages

### Client to Server
1. **`session_init`:**
   ```json
   {
     "type": "session_init",
     "meetingId": "meet-123",
     "platform": "google-meet",
     "audioSources": [0, 1],
     "sampleRate": 16000,
     "channels": 1,
     "encoding": "pcm_s16le",
     "clientVersion": "1.0.0",
     "timestamp": "2026-11-07T10:45:00Z"
   }
   ```
2. **`heartbeat`:** Sent every 15,000 ms to keep NAT/firewalls open.
3. **`capture_paused` / `capture_resumed`:** Informs backend of user pause state.
4. **`session_stop`:** Requests graceful closure and transitions session to `completed`.

### Server to Client
1. **`session_ready`:** Acknowledges session initialization.
2. **`audio_ack`:**
   ```json
   {
     "type": "audio_ack",
     "session_id": "meet-123",
     "sourceId": 0,
     "sequenceNumber": 42,
     "sampleCount": 2000,
     "receivedAt": "2026-11-07T10:45:01Z"
   }
   ```

---

## 3. Reconnection Strategy & Bounded Buffering

When a network drop occurs:
1. `ExtensionWebSocketService` enters state `reconnecting`.
2. **Exponential Backoff with Jitter:**
   $$ \text{delay} = \min(M, B \times 2^{\text{attempt}-1}) + \text{jitter} $$
   - Initial backoff $B = 1000$ ms.
   - Maximum backoff $M = 8000$ ms.
   - Jitter factor: $\pm 25\%$.
3. **Bounded Buffer:** During disconnections, incoming frames are stored in an in-memory ring buffer capped at **100 frames** (~12.5 seconds). If connection is not restored within this window, the oldest frames are dropped to prevent memory exhaustion, and a data gap is logged.

