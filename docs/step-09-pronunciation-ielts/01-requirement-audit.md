# Step 09 — Requirement Audit & Scope Boundaries

## 1. Executive Summary

Step 09 introduces the **Pronunciation Analysis & IELTS-Style English Assessment Engine** for FluentMeet AI. Spoken communication effectiveness depends not only on grammar, lexical choice, and syntactic fluency (evaluated in Step 08), but also fundamentally on acoustic clarity, phonemic production, syllable prominence, intonation modulation, speaking tempo, and international intelligibility.

This document establishes the audit criteria, scope boundaries, and core engineering principles guiding Step 09.

---

## 2. In-Scope Capabilities

| Capability | Module / Component | Engineering Standard |
| :--- | :--- | :--- |
| **Physical Audio Evidence Validation** | `AudioEvidenceValidator` | Strict SNR (> 10dB), clipping (< 5%), silence detection, duration verification. |
| **Dual-Track Audio Source Routing** | `SpeakerAudioResolver` | Source 0 (`local_mic`) vs Source 1 (`remote_mix`), cross-talk and overlap filtering. |
| **Word-Level Audio Alignment** | `WordAlignmentProcessor` | Boundary clamping, millisecond alignment, acoustic PCM slice extraction. |
| **Acoustic Phonetic Analysis** | `PhoneticAnalysisEngine` | ARPAbet/IPA phoneme contrasts, spectral energy ratios for fricatives (/θ/, /s/, /z/), plosive bursts, vowel Formants. |
| **Prosody & Intonation Modeling** | `ProsodyAnalysisEngine` | Normalized autocorrelation F0 pitch contour, pitch range, dynamic intonation classification, syllable stress prominence. |
| **Speaking Pace & Pause Taxonomy** | `SpeakingPaceAnalyzer` | Words-Per-Minute (WPM), syllables/min, speech-to-pause ratio, pause classification (`normal`, `short_hesitation`, `long_hesitation`, `boundary`). |
| **Speech Clarity & Intelligibility** | `IntelligibilityAnalyzer` | Accent-neutral composite scoring prioritizing international listener comprehension over native-speaker accent conformity. |
| **Deterministic Scoring Rubric** | `PronunciationScorer` | 0–100 scale, strict minimum 5 evaluated words gate, explicit separation of confidence and evidence coverage. |
| **IELTS-Style Practice Assessment** | `IELTSAssessmentEngine` | 4 Dimensions (Fluency, Lexical, Grammar, Pronunciation), 0.5 band rounding, CEFR/IELTS qualitative band descriptors, mandatory educational disclaimer. |
| **Actionable Improvement Drills** | `PronunciationRecommendationGenerator` | Minimal pair contrast drills (/θ/ vs /t/, /v/ vs /w/), syllable stress drills, speaking tempo modulation exercises. |
| **Contextual Feedback Explanation** | `PronunciationFeedbackEngine` | Google Gemini API with strict structured JSON schema, prompt isolation, and zero-hallucination guardrails. |
| **Relational Data Persistence** | PostgreSQL + Alembic `005` | Multi-tenant schema with 7 dedicated tables and cascading foreign keys. |
| **Asynchronous Stream Worker** | `PronunciationStreamConsumer` | Redis Stream `pronunciation:jobs` consumer group, dead-letter queue (DLQ), and automated stale message reclaim (`xautoclaim`). |
| **FastAPI REST Endpoints** | `app.api.v1.pronunciation` | Assessment trigger, status polling, word acoustic evidence, prosody metrics, recommendations, and IELTS estimates. |

---

## 3. Strict Out-of-Scope Boundaries

The following areas are explicitly excluded from Step 09 to preserve architectural modularity:
1. **Chrome Extension UI Redesign**: Extension recording is managed by Step 05; Step 09 is pure backend analysis.
2. **Audio Ingestion Protocol Redesign**: Audio WebSocket ingestion was perfected in Step 06; Step 09 consumes existing segments.
3. **Core ASR Model Training**: Whisper STT and PyAnnote diarization are consumed from Step 07.
4. **Official Certification Claims**: System outputs educational practice estimates only; no claims of certified IELTS or TOEFL examination.
5. **Accent Penalization**: Regional accents are never penalized; evaluation is strictly intelligibility-focused.

