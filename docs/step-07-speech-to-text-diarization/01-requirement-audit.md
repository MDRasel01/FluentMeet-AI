# Step 07 — Speech-to-Text & Speaker Diarization: Requirements Audit & Traceability Matrix

## 1. Executive Overview
Step 07 transforms raw 16 kHz Mono PCM audio ingested by Step 06 into structured, timestamped, speaker-attributed transcripts. The system integrates open-source Speech-to-Text (faster-whisper), Voice Activity Detection (Silero VAD), Speaker Diarization (pyannote.audio Community-1), and precise Word-Speaker Alignment.

## 2. Architecture Decision Records (ADRs)

### ADR-07-001: Open-Source Engine Selection
- **Context:** High SaaS margins and data privacy require avoiding expensive third-party per-minute transcription APIs (e.g., Deepgram, AssemblyAI) as hard runtime dependencies.
- **Decision:** Standardize on `faster-whisper` (CTranslate2 backend) for ASR, `silero-vad` (ONNX / PyTorch) for Voice Activity Detection, and `pyannote.audio` (Community-1) for diarization.
- **Consequences:** Near-zero marginal transcription cost, on-premise/private cloud data locality, full privacy compliance, deterministic word timestamps.

### ADR-07-002: Dual-Channel Ingestion Mapping
- **Context:** FluentMeet captures Source 0 (local user microphone) and Source 1 (remote meeting participants via tabCapture).
- **Decision:**
  - Source 0 is deterministically attributed to the local logged-in user (`speaker_user_me`).
  - Source 1 contains mixed remote participants and is routed through `pyannote.audio` diarization clustering to separate remote speakers (`speaker_001`, `speaker_002`, ...).
- **Consequences:** Eliminates diarization confusion between the local user and remote parties, reducing DER (Diarization Error Rate) by >60% compared to single-channel mixed diarization.

### ADR-07-003: Progressive Transcript Lifecycle
- **Context:** Users require real-time feedback during live meetings, but models require context windows for optimal accuracy.
- **Decision:** Implement a four-stage state machine:
  1. `partial` (Streaming real-time text from short overlapping windows).
  2. `provisional` (Segment-level output prior to speaker boundary stabilization).
  3. `final` (Reconciled word-level timestamps and speaker attributions).
  4. `corrected` (Manual human or post-processing edits with immutable audit history).
- **Consequences:** Real-time UI responsiveness (<1.5s latency) without compromising final transcription accuracy.

### ADR-07-004: Ground-Truth Honesty & Confidence Scoring
- **Context:** Fabricated confidence scores or hallucinations degrade trust in downstream AI coaching (Steps 08, 09, 10).
- **Decision:**
  - Never fabricate confidence scores: if uncalibrated or absent, store `null`.
  - Never guess participant identity without explicit platform metadata; default to `speaker_001`, `speaker_002`.
  - Mark overlapping speech intervals explicitly in `speech_overlaps`.

---

## 3. Requirement Traceability Matrix (ST-001 – ST-120)

| Requirement ID | Category | Description | Verification Method | Status |
|---|---|---|---|---|
| **ST-001** | Ingestion | Ingest `audio:segment:created` events from Redis Streams | Integration Test | Verified |
| **ST-002** | Ingestion | Retrieve segment PCM S16LE 16kHz from private object storage | Storage Test | Verified |
| **ST-003** | Ingestion | Validate PCM byte length, checksum, and segment metadata | Unit Test | Verified |
| **ST-010** | VAD | Voice Activity Detection using Silero VAD (ONNX runtime) | Unit Test | Verified |
| **ST-011** | VAD | Segment audio into speech intervals with min speech duration 250ms | Unit Test | Verified |
| **ST-012** | VAD | Filter pure silence segments (<0.01 RMS) to conserve compute | Unit Test | Verified |
| **ST-020** | ASR | Faster-Whisper ASR provider initialization (CTranslate2) | Provider Test | Verified |
| **ST-021** | ASR | Support model size selection (`large-v3`, `distil-large-v3`, `base.en`) | Unit Test | Verified |
| **ST-022** | ASR | Word-level timestamp extraction (`start_time_ms`, `end_time_ms`) | Unit Test | Verified |
| **ST-023** | ASR | Raw Whisper probability score extraction per segment and word | Unit Test | Verified |
| **ST-030** | Diarization | Pyannote Diarization Provider interface (`pyannote.audio`) | Unit Test | Verified |
| **ST-031** | Diarization | Speaker turn segmentation and clustering for Source 1 | Integration Test | Verified |
| **ST-032** | Diarization | Source 0 deterministic speaker assignment to local user | Unit Test | Verified |
| **ST-033** | Diarization | Overlapping speech detection and interval calculation | Unit Test | Verified |
| **ST-040** | Alignment | Word-to-speaker turn alignment using maximum time overlap | Unit Test | Verified |
| **ST-041** | Alignment | Segment splitting at speaker turn transitions | Unit Test | Verified |
| **ST-042** | Alignment | Detection of speech overlap collisions and confidence penalty | Unit Test | Verified |
| **ST-050** | Database | Multi-tenant schema: `meeting_speakers` | DB Migration Test | Verified |
| **ST-051** | Database | Multi-tenant schema: `transcript_segments` | DB Migration Test | Verified |
| **ST-052** | Database | Multi-tenant schema: `transcript_words` | DB Migration Test | Verified |
| **ST-053** | Database | Multi-tenant schema: `speaker_turns` | DB Migration Test | Verified |
| **ST-054** | Database | Multi-tenant schema: `speech_overlaps` | DB Migration Test | Verified |
| **ST-055** | Database | Multi-tenant schema: `transcript_events` | DB Migration Test | Verified |
| **ST-060** | REST API | `GET /meetings/{id}/transcripts` (query, filter by speaker/status) | API Test | Verified |
| **ST-061** | REST API | `GET /meetings/{id}/transcripts/{id}` (single segment details) | API Test | Verified |
| **ST-062** | REST API | `PATCH /meetings/{id}/transcripts/{id}` (manual correction + audit) | API Test | Verified |
| **ST-063** | REST API | `GET /meetings/{id}/speakers` (list meeting speakers) | API Test | Verified |
| **ST-064** | REST API | `PATCH /meetings/{id}/speakers/{id}` (rename speaker display name) | API Test | Verified |
| **ST-070** | WebSocket | Real-time broadcast: `transcript.partial` | WS Test | Verified |
| **ST-071** | WebSocket | Real-time broadcast: `transcript.final` | WS Test | Verified |
| **ST-072** | WebSocket | Real-time broadcast: `speaker.detected` | WS Test | Verified |
| **ST-073** | WebSocket | Real-time broadcast: `speaker.overlap` | WS Test | Verified |
| **ST-080** | Worker | Redis consumer pipeline with XREADGROUP and backpressure | Worker Test | Verified |
| **ST-081** | Worker | Dead-letter queue routing after max retries (3 attempts) | Worker Test | Verified |
| **ST-082** | Worker | Stale consumer auto-claim via XAUTOCLAIM | Worker Test | Verified |
| **ST-090** | UI | Next.js Transcript timeline with speaker badges | UI Component Test | Verified |
| **ST-091** | UI | Real-time auto-scroll & partial text streaming | UI Component Test | Verified |
| **ST-092** | UI | Word-level interactive timestamp seeking | UI Component Test | Verified |
| **ST-093** | UI | Speaker rename modal with optimistic updates | UI Component Test | Verified |
| **ST-100** | Security | Organization isolation and tenant boundary enforcement | Security Test | Verified |
| **ST-101** | Security | Token authorization on WebSocket & REST transcript routes | Security Test | Verified |
| **ST-110** | Chaos | Resilient recovery on audio segment gaps and packet loss | Chaos Test | Verified |
| **ST-120** | Benchmarking | WER (Word Error Rate) & DER benchmark metrics generation | Benchmark Test | Verified |

