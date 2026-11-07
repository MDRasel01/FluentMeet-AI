# WebSocket Binary & Control Protocol Specification

## 1. Binary Audio Frame Layout

The binary framing layout maintains strict bit-level parity between the Step 05 Chrome Extension (`audio-encoder.ts`) and Step 06 backend (`protocol.py`). All multibyte integer and float fields are formatted using **Network Byte Order (Big-Endian)**.

### Header Byte Map (23 + N Bytes)

| Byte Offset | Field Name | Data Type | Endianness | Permitted Values & Description |
| :--- | :--- | :--- | :--- | :--- |
| `00` | `protocol_version` | Uint8 | — | Must be `1` |
| `01` | `source_id` | Uint8 | — | `0` = Remote Tab Audio, `1` = Local Mic Audio |
| `02..05` | `sequence_number` | Uint32 | Big-Endian | Strictly monotonic sequence (1, 2, 3...) per source |
| `06..13` | `timestamp_ms` | Float64 | Big-Endian | Session-relative start time in milliseconds |
| `14..15` | `sample_rate` | Uint16 | Big-Endian | Negotiated rate, must be `16000` Hz |
| `16` | `channels` | Uint8 | — | Channel count, must be `1` (Mono) |
| `17` | `encoding` | Uint8 | — | `1` = Raw Linear PCM 16-bit Signed LE (`pcm_s16le`) |
| `18..21` | `sample_count` | Uint32 | Big-Endian | Number of 16-bit audio samples in the payload |
| `22` | `meeting_id_len` | Uint8 | — | Length $N$ of UTF-8 meeting identifier string (1..255) |
| `23..23+N-1` | `meeting_id` | Bytes | UTF-8 | Meeting identifier string |
| `23+N..End` | `pcm_payload` | Bytes | Little-Endian | Raw PCM S16LE audio bytes ($2 \times \text{sample\_count}$) |

---

## 2. Two-Tier Acknowledgement Architecture

To satisfy real-time client responsiveness while ensuring strict durability guarantees, FluentMeet AI employs a two-tier acknowledgement protocol:

### Level 1: `audio_received` (Low Latency / Immediate Ingestion ACK)
Sent immediately after the backend decodes the binary framing, validates the PCM format, records sequence monotonicity, and updates timeline drift metrics.

```json
{
  "type": "audio_received",
  "status": "accepted",
  "session_id": "meet-614ef-908a",
  "sourceId": 0,
  "sequenceNumber": 105,
  "sampleCount": 1600,
  "clockDriftMs": 2.45,
  "receivedAt": "2026-11-07T06:15:00.120450Z"
}
```

* **Client Reaction:** Extension marks chunk as accepted and keeps its local transmission ring-buffer pointer moving forward.

### Level 2: `audio_persisted` (Durability ACK)
Sent only after an accumulated 1.0–5.0s audio segment (default 3000ms) has been:
1. Written atomically to private object storage.
2. Verified with SHA-256 checksum matching.
3. Committed to PostgreSQL metadata tables.
4. Published to Redis Streams event bus.

```json
{
  "type": "audio_persisted",
  "session_id": "meet-614ef-908a",
  "segmentId": "28d9cb16-4354-466a-8841-6ffd31a98fd8",
  "sourceId": 0,
  "durationMs": 3000,
  "sampleCount": 48000,
  "checksum": "686d4b0e6b87db8e279d3822aa44189000ee4a2328858275ef9e930576b3ca00",
  "storageKey": "organizations/org-1/meetings/meet-614ef-908a/streams/stream-0/sources/0/segments/28d9cb16-4354-466a-8841-6ffd31a98fd8.pcm",
  "redisMessageId": "1762500000000-0"
}
```

* **Client Reaction:** Extension purges the acknowledged sequence range (`first_sequence..last_sequence`) from its local IndexedDB failure recovery store.

---

## 3. Control & Lifecycle Messages

### Handshake & Session Initialization
```json
// Client -> Backend (Handshake)
GET /ws/meetings/{meeting_id}/audio?token={jwt}&org_id={org}

// Backend -> Client (ACK)
{
  "type": "connection_ack",
  "session_id": "meet-614ef-908a",
  "user_id": "usr-881b-520c",
  "organization_id": "org-1",
  "connected_at": "2026-11-07T06:14:55.002130Z",
  "status": "ready"
}
```

### Heartbeat
* Client sends: `{"type": "ping"}`
* Backend responds: `{"type": "pong", "timestamp": "2026-11-07T06:15:05.102Z"}`

### Session Stop & Flush
* Client sends: `{"type": "session_stop"}`
* Backend flushes uncommitted buffer chunks for Source 0 and Source 1, dispatches any final `audio_persisted` events, and finishes with:
```json
{
  "type": "session_completed",
  "session_id": "meet-614ef-908a",
  "flushed_segments_count": 2,
  "status": "completed",
  "timestamp": "2026-11-07T06:20:00.000Z"
}
```
