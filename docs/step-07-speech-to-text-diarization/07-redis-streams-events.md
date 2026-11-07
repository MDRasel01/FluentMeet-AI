# Step 07 — Redis Streams & Real-Time Event Architecture

## 1. Overview
Redis Streams provides durable, at-least-once event delivery decoupling audio segment ingestion (Step 06) from transcription and diarization workers (Step 07).

## 2. Stream Definitions

| Stream Name | Consumer Group | Payload Origin | Consumer Action |
|---|---|---|---|
| `audio:segments` | `transcription_workers` | Step 06 WebSocket ingestion | Triggers VAD, ASR, and Diarization pipeline |
| `meeting:{id}:events` | Distributed WebSocket Hub | Step 07 Transcription Service | Delivers live events to browser clients |
| `audio:segments:dlq` | Operations / Monitor | Worker retry failure handler | Dead-letter storage for unparseable segments |

## 3. Event Payloads

### 3.1 `transcript.final`
```json
{
  "type": "transcript.final",
  "meeting_id": "meet-uuid-123",
  "payload": {
    "id": "seg-uuid-456",
    "meeting_id": "meet-uuid-123",
    "speaker_id": "spk-uuid-789",
    "speaker_label": "speaker_user_me",
    "display_name": "You (Host)",
    "source_id": 0,
    "start_time_ms": 12000,
    "end_time_ms": 15400,
    "text": "Let's review the quarterly revenue milestones.",
    "confidence_score": 0.965,
    "status": "final",
    "words": [
      {
        "word": "Let's",
        "start_time_ms": 12000,
        "end_time_ms": 12400,
        "confidence_score": 0.98
      }
    ]
  }
}
```

### 3.2 `speaker.detected`
```json
{
  "type": "speaker.detected",
  "meeting_id": "meet-uuid-123",
  "payload": {
    "speaker_id": "spk-uuid-888",
    "speaker_label": "speaker_001",
    "display_name": "Speaker 001",
    "source_id": 1
  }
}
```

### 3.3 `speaker.overlap`
```json
{
  "type": "speaker.overlap",
  "meeting_id": "meet-uuid-123",
  "payload": {
    "meeting_id": "meet-uuid-123",
    "start_time_ms": 14200,
    "end_time_ms": 15000,
    "overlapping_speakers": ["speaker_user_me", "speaker_001"],
    "confidence_score": 0.92
  }
}
```

## 4. Resiliency & Consumer Groups
- **At-Least-Once Delivery:** Messages are only acknowledged (`XACK`) after successful database commit.
- **Dead-Letter Routing:** Messages failing 3 consecutive attempts are automatically moved to `audio:segments:dlq` with failure timestamps and stack trace metadata.
- **Stale Claiming:** `claim_stale_messages` periodically executes `XAUTOCLAIM` with an idle threshold of 30 seconds to recover messages from crashed or killed worker processes.
