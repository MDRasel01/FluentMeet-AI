# Known Limitations & Step 07 Handover Boundaries

## 1. Architectural Scope Boundaries

Step 06 strictly implements **Audio Ingestion, Validation, Synchronization, Buffering, Durable Storage, and Worker Event Transport**.
The following capabilities are deliberately scoped to subsequent development steps:

1. **Speech-to-Text (ASR) & Transcription (Step 07):**
   * Step 06 delivers validated, synchronized 16 kHz Mono PCM segments with SHA-256 integrity into private object storage and emits `audio:segment:created` events into Redis Streams.
   * Integration with Deepgram Nova-2 / Whisper API for real-time phoneme and word-level timestamp generation is the core objective of Step 07.

2. **Acoustic Speaker Diarization (Step 07):**
   * Separation of Remote Tab Audio (Source 0) into distinct meeting participants (Interviewer 1, Interviewer 2, etc.) occurs in Step 07 using PyAnnote or Deepgram diarization models.

3. **Live CEFR Coaching Feedback & UI Push (Step 08):**
   * Real-time push of vocabulary suggestions, grammar corrections, and pace hints back to the Chrome Extension floating panel is driven by the Step 08 LLM evaluation pipeline.

---

## 2. Documented Operational Limits

* **Maximum Ingestion Buffer:** Buffers are clamped to `max_buffer_chunks = 100` (~10 seconds). Clients failing to process backpressure notifications within this window will experience frame drops to protect server memory stability.
* **Target Segment Size:** Configured to `3000 ms` (3.0 seconds). Durations shorter than 1000 ms increase S3 API transaction overhead; durations longer than 5000 ms introduce undesirable latency for real-time transcription.
* **Reconnection Window:** Extension ring buffers preserve up to 30 seconds of audio during network reconnects. Disconnections exceeding 30 seconds result in a detected sequence gap logged to `audio_stream_gaps`.
