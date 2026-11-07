# Step 07 — Error Handling & Pipeline Resiliency

## 1. Failure Modes & Mitigations

| Failure Scenario | Root Cause | System Mitigation Strategy |
|---|---|---|
| **Audio Segment Silence** | User muted, room quiet | VAD provider detects empty speech intervals; returns `{status: "silence"}` immediately without running GPU/CPU ASR. |
| **Worker Crash During Processing** | OOM or host termination | Message remains unacknowledged in Redis Stream; periodic `XAUTOCLAIM` reclaims pending message after 30s. |
| **Corrupted Object Storage File** | Incomplete write or bad key | Checksum validation catches corruption before processing; raises `FileNotFoundError` and triggers DLQ routing. |
| **Acoustic Overlap Collision** | Simultaneous cross-talk | System marks interval in `speech_overlaps`, attributes words to primary turn, and penalizes confidence. |
| **Whisper Hallucination / Drift** | Extended background noise | Repetition penalty and dynamic temperature fallback; segments with `avg_logprob < -1.0` tagged for manual review. |

## 2. Dead-Letter Queue (DLQ) Topology
When a segment fails processing across 3 consecutive retry attempts:
1. Message data is copied with:
   - `b"error_reason"`: Exact exception message and type.
   - `b"failed_at"`: UTC ISO-8601 timestamp.
   - `b"original_message_id"`: Redis Stream ID.
2. Written via `XADD` to `audio:segments:dlq`.
3. Message acknowledged (`XACK`) from primary stream `audio:segments` to avoid head-of-line blocking.
4. Sentry / alert monitor triggered for engineer inspection.
