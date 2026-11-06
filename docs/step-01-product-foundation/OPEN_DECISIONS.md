# Open Technical Decisions & Architectural Trade-offs (TDR)

**Product Name:** AI Meeting English Coach  
**Document ID:** TDR-OPEN-V1.0  
**Status:** Active Technical Decision Records  
**Version:** 1.0.0  

---

## 1. Decision Registry Summary

The following architectural choices have been rigorously analyzed. To adhere to strict engineering principles, these items are logged as **OPEN DECISIONS** with clear evaluation criteria rather than making unverified assumptions.

| Decision ID | Domain | Topic | Recommended Direction | Resolution Step |
|---|---|---|---|:---:|
| **DEC-001** | Audio / ASR | Speech-to-Text Engine Selection | Deepgram Nova-2 (Primary) / Whisper (Fallback) | Step 07 |
| **DEC-002** | Audio / AI | Speaker Diarization Strategy | Deepgram Built-in Diarization (MVP) | Step 07 |
| **DEC-003** | AI / Acoustics | Pronunciation Assessment Engine | Azure Speech Pronunciation Assessment (v1.1) | Step 09 |
| **DEC-004** | Extension | Dual-Stream Audio Track Architecture | Dual-Channel Stereo (Left: Mic, Right: Tab) | Step 06 |
| **DEC-005** | Backend | Processing Mode (Streaming vs Batch) | Post-Meeting Batch Pipeline for MVP | Step 06 |
| **DEC-006** | Product / Legal| Cross-Platform Consent Workflow | In-Extension Mandatory User Confirmation | Step 05 |
| **DEC-007** | Infrastructure | Audio Storage & Retention Tiering | Default 7-Day Ephemeral Retention | Step 03 |

---

## 2. Technical Decision Records

### DEC-001: Speech-to-Text (ASR) Engine Selection
- **Context:** We need high-accuracy, cost-effective transcription with millisecond word-level timestamps.
- **Options Considered:**
  1. *OpenAI Whisper API:* High accuracy across diverse accents, but higher latency and cost ($0.006/min).
  2. *Deepgram Nova-2:* Extremely fast (sub-300ms latency), native word-level timestamps, lower cost ($0.0043/min), built-in diarization option.
  3. *Self-Hosted Whisper on GPU (vLLM / Faster-Whisper):* Zero per-minute API cost, but requires dedicated GPU cluster management ($600+/mo base cost).
- **Recommended Direction for MVP:** **Deepgram Nova-2** for MVP due to native word timestamps and predictable per-minute billing. Self-hosted Whisper evaluated for v2.0 scale.
- **Resolution Milestone:** Step 07 (Speech-to-Text Engine Integration).

---

### DEC-002: Speaker Diarization Strategy
- **Context:** Meetings involve 2 to 10 participants speaking sequentially or overlapping. The system must cluster who spoke when.
- **Options Considered:**
  1. *Deepgram Diarization (Integrated with ASR):* Single API call for both transcription and speaker tagging. Simplifies worker pipeline.
  2. *PyAnnote Audio (Self-Hosted):* State-of-the-art open-source diarization, but high GPU compute requirements.
  3. *Gemini Multimodal Direct Audio Diarization:* Gemini 1.5/2.0 can process audio directly, but timestamp alignment is less granular than dedicated diarizers.
- **Recommended Direction for MVP:** **Deepgram Integrated Diarization** for MVP to avoid maintaining separate GPU diarization infrastructure.
- **Resolution Milestone:** Step 07.

---

### DEC-003: Pronunciation Assessment Engine
- **Context:** Pronunciation scoring requires comparing raw spoken audio phonemes against ground-truth native phoneme models. Text-only evaluation is strictly forbidden.
- **Options Considered:**
  1. *Azure Speech Pronunciation Assessment API:* Mature, industry standard, provides phoneme-level accuracy, fluency, and prosody scores. Cost: ~$1.00 per audio hour.
  2. *Wav2Vec2 / Kaldi Forced Alignment:* Open source, requires hosting acoustic alignment pipelines.
  3. *Gemini Audio Ingestion:* Can identify general pronunciation clarity from raw audio tokens, but lacks phoneme-by-phoneme IPA scoring.
- **Recommended Direction for MVP / v1.1:** Defer deep acoustic phoneme scoring to **Version 1.1** using **Azure Speech Pronunciation Assessment**, keeping MVP focused on Grammar, Vocabulary, and Fluency.
- **Resolution Milestone:** Step 09 (Pronunciation Evaluation Engine).

---

### DEC-004: Dual-Stream Audio Track Architecture
- **Context:** We capture two distinct streams in the extension: (1) Local user microphone and (2) Remote meeting participants (tab audio).
- **Options Considered:**
  1. *Mono Mixdown:* Merge mic and tab audio into a single mono 16kHz PCM stream. Simpler upload, but diarization must distinguish the user from others acoustically.
  2. *Stereo Channel Separation:* Encode Local Mic on Channel 0 (Left) and Tab Audio on Channel 1 (Right). Perfectly isolates the user from all remote participants with 100% confidence.
- **Recommended Direction for MVP:** **Stereo Channel Separation**. This guarantees that the user's speech is never misattributed to other meeting participants.
- **Resolution Milestone:** Step 06 (Audio Capture & Streaming Engine).

---

### DEC-005: Real-time Streaming ASR vs. Post-Meeting Batch Processing
- **Context:** Should we transcribe audio in real time during the meeting or batch-process upon call termination?
- **Options Considered:**
  1. *Real-time Streaming ASR:* Transcribes continuously while the meeting is live. Higher WebSocket overhead and API cost; higher failure risk if network drops.
  2. *Post-Meeting Batch Processing:* Stream raw audio chunks to cloud storage during the call; trigger full ASR + Diarization + Gemini analysis upon clicking "Stop & Analyze".
- **Recommended Direction for MVP:** **Post-Meeting Batch Pipeline**. Reduces complexity, tolerates network drops cleanly, and matches the product use case (reviewing reports after the meeting).
- **Resolution Milestone:** Step 06.

---

### DEC-006: Cross-Platform Participant Consent Workflow
- **Context:** Wiretapping laws in several jurisdictions require all-party consent. How should consent be obtained without injecting bots into meeting rooms?
- **Options Considered:**
  1. *Automated In-Meeting Chat Notification:* Content script posts an automated message to the meeting chat: *"Notice: AI Meeting English Coach is active."* (May annoy users or be flagged by platform bots).
  2. *Extension Enforced User Assertion:* The user is legally prompted with a mandatory, blocking confirmation checkbox in the extension side panel before recording arms.
- **Recommended Direction for MVP:** **Extension Enforced User Assertion (Option 2)**, logging the user's cryptographic consent assertion and timestamp.
- **Resolution Milestone:** Step 05 (Chrome Extension Development).

---

### DEC-007: Audio Storage & Retention Tiering
- **Context:** Storing large volumes of uncompressed audio creates significant cloud storage costs and data privacy exposure.
- **Options Considered:**
  1. *Permanent Storage:* Keep all meeting audio forever in S3. High storage cost; higher security liability.
  2. *Default 7-Day Ephemeral Retention:* Store stitched audio in S3 for 7 days (to allow playback during report review), then automatically purge audio while preserving text transcripts and reports indefinitely.
- **Recommended Direction for MVP:** **Default 7-Day Ephemeral Retention** with configurable settings in `/settings/privacy`.
- **Resolution Milestone:** Step 03 (Infrastructure & Database Setup).

