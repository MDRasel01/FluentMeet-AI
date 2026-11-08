# Step 09 — Audio Evidence Validation & Quality Gates

## 1. Overview & Architectural Principle

A fundamental rule of Step 09 is that **pronunciation scores must never be fabricated from transcript text alone**. Every evaluation requires physical acoustic evidence captured during the meeting.

The `AudioEvidenceValidator` and `SpeakerAudioResolver` serve as the pre-analysis validation gates, ensuring that audio files exist, are accessible, have valid signal-to-noise ratios, and are correctly attributed to the speaking participant.

---

## 2. Audio Integrity Metrics

The validator computes four core acoustic integrity metrics from raw 16-bit 16kHz PCM audio buffers:

| Metric | Calculation Method | Threshold | Impact of Violation |
| :--- | :--- | :--- | :--- |
| **Duration** | Sample count / sample rate | $\ge 1000\text{ ms}$ | Flagged as `insufficient_speech`; evaluation halted. |
| **Clipping Ratio** | Fraction of samples with $\|A\| \ge 0.999$ | $< 0.15$ (15%) | Flagged as `low_quality` due to distortion. |
| **Silence Ratio** | Fraction of 50ms frames with $\text{RMS} < -45\text{ dBFS}$ | $< 0.95$ (95%) | Flagged as `insufficient_speech`. |
| **SNR (dB)** | $20 \log_{10}(\text{Peak Energy} / \text{Noise Floor})$ | $\ge 6.0\text{ dB}$ | If $< 6.0\text{ dB}$, flagged as `high_noise`. |

---

## 3. Dual-Track Audio Source Routing

Participants in FluentMeet AI are recorded via two distinct streams:
1. **Source 0 (`local_mic`)**: Dedicated microphone stream capturing the local user. Provides high SNR, isolated audio with zero acoustic echo.
2. **Source 1 (`remote_mix`)**: Tab audio capturing remote meeting participants, diarized via PyAnnote in Step 07.

The `SpeakerAudioResolver` enforces the following routing logic:
- If `speaker_label` matches the local user (`speaker_user_me` or `source_id == 0`), prioritize `local_mic` (attribution confidence $0.98$). Fallback to `remote_mix` only if local microphone capture was unavailable.
- For remote participants, map to `remote_mix` (source 1). Require diarization confidence $\ge 0.60$. If diarization confidence $< 0.60$, the speaker is marked `uncertain` (`LOW_DIARIZATION_CONFIDENCE`) to prevent attributing misidentified speech.
- Overlapping speech segments (where multiple participants speak simultaneously) are detected from `SpeechOverlap` records and excluded from word-level phoneme scoring to prevent acoustic corruption.
