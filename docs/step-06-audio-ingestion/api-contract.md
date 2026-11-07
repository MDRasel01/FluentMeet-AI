# REST & WebSocket API Contract

## 1. REST Endpoints Specification

Base Path: `/api/v1`

### 1. Register Audio Stream
* **Route:** `POST /meetings/{meeting_id}/audio-streams`
* **Auth:** Bearer JWT required.
* **Request:**
  ```json
  {
    "source_id": 0,
    "codec": "pcm_s16le",
    "sample_rate": 16000,
    "channels": 1
  }
  ```
* **Response (200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "id": "stream-uuid-1",
      "meeting_id": "meet-1",
      "source_id": 0,
      "stream_id": "stream-0-abc",
      "codec": "pcm_s16le",
      "sample_rate": 16000,
      "channels": 1,
      "status": "active"
    },
    "message": "Audio stream initialized"
  }
  ```

### 2. List Meeting Streams
* **Route:** `GET /meetings/{meeting_id}/audio-streams`
* **Response (200 OK):** Returns array of `AudioStreamResponse` objects for Pipeline A and Pipeline B.

### 3. Get Stream Metadata
* **Route:** `GET /audio-streams/{stream_id}`
* **Response (200 OK):** Returns single `AudioStreamResponse`.

### 4. List Stream Segments
* **Route:** `GET /audio-streams/{stream_id}/segments?limit=50&offset=0`
* **Response (200 OK):** Returns paginated list of `AudioSegmentResponse` with embedded quality metrics.

### 5. Get Segment Details
* **Route:** `GET /audio-segments/{segment_id}`
* **Response (200 OK):** Detailed segment metadata, checksum, storage key, and acoustic quality analysis.

### 6. Meeting Ingestion Status
* **Route:** `GET /meetings/{meeting_id}/audio-status`
* **Response (200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "meeting_id": "meet-1",
      "status": "active",
      "active_sources": [0, 1],
      "source_stats": {
        "0": {"segments_count": 12, "duration_ms": 36000, "bytes": 1152000, "last_sequence": 360},
        "1": {"segments_count": 8, "duration_ms": 24000, "bytes": 768000, "last_sequence": 240}
      },
      "total_segments": 20,
      "total_duration_ms": 60000,
      "total_bytes": 1920000,
      "total_gaps_detected": 0
    }
  }
  ```

### 7. Meeting Audio Quality
* **Route:** `GET /meetings/{meeting_id}/audio-quality`
* **Response (200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "meeting_id": "meet-1",
      "overall_quality": "EXCELLENT",
      "total_segments_analyzed": 20,
      "average_rms": 0.2845,
      "peak_amplitude": 0.6512,
      "average_clipping_ratio": 0.0000,
      "average_silence_ratio": 0.1200,
      "degraded_segments_count": 0,
      "details_by_source": {
        "0": {"segments_count": 12, "average_rms": 0.3100, "peak_amplitude": 0.6512},
        "1": {"segments_count": 8, "average_rms": 0.2462, "peak_amplitude": 0.5200}
      }
    }
  }
  ```

### 8. Close Audio Stream
* **Route:** `POST /audio-streams/{stream_id}/close`
* **Response (200 OK):** Flushes remaining chunks and returns flushed segment count.

---

## 2. WebSocket Streaming Contract

* **Endpoint:** `GET /ws/meetings/{meeting_id}/audio?token={jwt}`
* **Protocols:** Text JSON Control and Binary PCM Framing (Section 12.1).
