# Product Overview & Core Vision

**Product Name:** AI Meeting English Coach  
**Document ID:** SPEC-OVERVIEW-V1.0  
**Status:** Approved Foundation  
**Version:** 1.0.0  

---

## 1. Product Vision

**AI Meeting English Coach** is an intelligent, multi-tenant AI SaaS platform that analyzes spoken English during virtual meetings and delivers deeply personalized, actionable feedback to accelerate language proficiency in professional workplace environments.

By operating unobtrusively in the background via a modern Chrome Extension (Manifest V3), the platform captures meeting audio, identifies distinct speakers, and feeds diarized transcripts into Google Gemini and specialized acoustic models. Following each session, participants access a sophisticated Web Dashboard that transforms real workplace conversations into targeted learning opportunities.

```
       [ Live Meeting in Browser ]
         (Meet / Zoom / Teams)
                  │
                  ▼
     [ Chrome SidePanel Extension ]
  (Audio Capture + Participant Discovery)
                  │
                  ▼ (Secure WebSockets)
        [ Cloud AI Pipeline ]
  (ASR + Diarization + Gemini AI Engine)
                  │
                  ▼
         [ Web Dashboard ]
  (Interactive Reports & Micro-Lessons)
```

---

## 2. Core Product Objectives

1. **Automated Meeting Capture:** Capture high-fidelity dual-stream audio (system/tab audio + local microphone) directly from web-based meeting sessions without injecting disruptive bots into virtual rooms.
2. **Speaker Identification & Diarization:** Separate and isolate individual voices across the meeting timeline, assigning distinct acoustic clusters to corresponding participants.
3. **Identity-to-Speaker Mapping:** Map acoustic voice clusters to actual participant names scraped safely from the meeting DOM, with explicit confidence scoring and manual verification fallbacks.
4. **Multi-Faceted English Analysis:** Evaluate spoken English across four foundational pillars:
   - **Grammar & Syntactic Accuracy**
   - **Vocabulary Range & Contextual Appropriateness**
   - **Fluency, Pacing & Speech Dynamics**
   - **Pronunciation & Articulatory Clarity**
5. **Evidence-Based Feedback Delivery:** Provide timestamped, audio-synced corrections showing exactly what was said, why it was sub-optimal, and how to express the thought with native professional polish.
6. **Individual & Team Performance Visibility:** Supply private, psychologically safe reporting for individual professionals while delivering aggregated, non-punitive skill gap analytics for enterprise team leads.
7. **Longitudinal Progress Tracking:** Quantify linguistic growth over time (30, 60, 90 days), tracking the reduction of persistent mistake categories and vocabulary expansion.
8. **Enterprise SaaS Multi-Tenancy & Usage Metering:** Provide robust subscription management, seat allocation, role-based access control (RBAC), and multi-dimensional usage tracking (meeting minutes, audio processing minutes, AI token consumption).

---

## 3. Supported Platforms & Boundary Architecture

### 3.1 Initial Phase (Web Browser Meeting Clients)
In the initial development phases (MVP v1.0 and v1.1), the product strictly supports **Browser-based Web Versions** running inside Google Chrome:
- **Google Meet Web** (`https://meet.google.com/*`) — *Primary Target for MVP v1.0*
- **Zoom Web Client** (`https://app.zoom.us/wc/*`, `https://*.zoom.us/*`) — *MVP v1.0 compatibility probe, v1.1 official support*
- **Microsoft Teams Web** (`https://teams.microsoft.com/*`) — *MVP v1.0 compatibility probe, v1.1 official support*

### 3.2 Explicit Platform Boundary: Desktop Apps vs. Browser Extension
> [!IMPORTANT]
> The Chrome Extension captures audio exclusively from the active browser tab via `chrome.tabCapture` and the local microphone via `navigator.mediaDevices.getUserMedia`. 
> 
> **It CANNOT capture audio from standalone desktop applications** (such as Zoom Desktop Client for Windows/macOS or Microsoft Teams Desktop App). 
> 
> The engineering team and marketing materials must never promise desktop client capture within the Chrome Extension. Capturing desktop client audio is explicitly deferred to Phase 3 (v2.0) as a standalone Desktop Companion Application (Electron / Native C++ audio driver).

---

## 4. The Four Core Analysis Pillars

```
                     ┌──────────────────────────────────┐
                     │    AI English Coaching Engine    │
                     └────────────────┬─────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │                            │                            │
         ▼                            ▼                            ▼
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│ Grammar & Syntax │         │ Vocabulary Range │         │ Fluency Dynamics │
│                  │         │                  │         │                  │
│ • Tense Shift    │         │ • Repetition     │         │ • WPM Dynamics   │
│ • Prepositions   │         │ • Executive Tone │         │ • Filler Words   │
│ • Agreement      │         │ • Idiomatic Fits │         │ • Pause Lengths  │
└──────────────────┘         └──────────────────┘         └──────────────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │  Pronunciation   │
                             │                  │
                             │ • Phonetic Error │
                             │ • Word Stress    │
                             │ • IPA Guidance   │
                             └──────────────────┘
```

### 4.1 Pillar 1: Grammar & Syntactic Accuracy
- **Tense & Aspect Consistency:** Identifies jarring shifts between past simple, present perfect, and past continuous.
- **Subject-Verb Agreement:** Flags plural/singular mismatches, particularly in complex multi-clause sentences.
- **Preposition Precision:** Corrects subtle errors common in non-native speech (e.g., "explain me this" $\to$ "explain this to me"; "discussed about" $\to$ "discussed").
- **Sentence Boundaries:** Flags incomplete fragments, dangling modifiers, and excessive run-on sentences.

### 4.2 Pillar 2: Vocabulary & Lexical Precision
- **Repetitive Word Detection:** Highlights overused modifiers (e.g., using "very good", "important", or "issue" dozens of times) and suggests dynamic alternatives.
- **Contextual Formality & Executive Tone:** Replaces overly casual idioms or direct, abrasive phrasing with diplomatic professional phrasing (e.g., replacing "You are wrong about the deadline" with "I have a different read on our delivery timeline").
- **Domain-Specific Fluency:** Recommends industry-standard business and technical terminology suitable for executive presentations.

### 4.3 Pillar 3: Fluency & Temporal Dynamics
- **Speaking Pacing (Words Per Minute):** Evaluates speech speed against the recommended professional baseline (130–160 WPM). Flags hyper-rapid delivery caused by nervousness or lethargic pacing.
- **Filler Word Density:** Measures the frequency and ratio of disfluencies ("um", "uh", "you know", "like", "actually") against total spoken words.
- **Hesitation & Silent Pauses:** Analyzes pauses longer than 2.0 seconds to distinguish between deliberate rhetorical pauses and hesitations caused by cognitive vocabulary search.

### 4.4 Pillar 4: Pronunciation & Articulatory Clarity
- **Acoustic & Phonetic Evaluation:** Identifies phoneme substitution patterns (e.g., /v/ vs /w/, /θ/ vs /s/, /r/ vs /l/) where acoustic modeling is active.
- **Word Stress & Intonation:** Highlights incorrect syllable stress in multi-syllabic professional terms (e.g., `de-VEL-op-ment` vs `DEV-el-op-ment`).
- **Phonetic IPA & Audio Clones:** Presents International Phonetic Alphabet (IPA) transcriptions and clear native reference audio playback.

---

## 5. IELTS-Style Speaking Assessment Framework

For users preparing for formal benchmarks or seeking standardized self-evaluation, the platform translates real meeting speech into estimated **IELTS-style Band Scores (0.0 to 9.0)**:

| Category | Assessment Criteria | Equivalent Scoring Metrics |
|---|---|---|
| **Fluency & Coherence** | Speech continuity, logical signposting, natural linking words, absence of disruptive hesitations. | Pauses per minute, filler ratio, discourse marker variety. |
| **Lexical Resource** | Breadth of professional vocabulary, precision of word choice, ability to paraphrase, avoidance of repetition. | Type-Token Ratio (TTR), academic/C1-C2 vocabulary index. |
| **Grammatical Range & Accuracy** | Variety of complex sentence structures, clause subordination, error-free sentence ratio. | Compound sentence %, error density per 100 words. |
| **Pronunciation** | Phoneme clarity, rhythm, intonation, comprehensibility without listener strain. | Acoustic phonetic accuracy score, stress accuracy. |

> [!WARNING]
> **Strict Regulatory Disclaimer:**
> The Web Dashboard and Reports must explicitly display the following statement:  
> *"This evaluation is an AI-assisted estimate designed for self-improvement and professional benchmarking. It is neither affiliated with nor endorsed by IELTS™, British Council, IDP, or Cambridge Assessment English."*

---

## 6. Ethical AI Principles & Anti-Bias Commitments

1. **No Scoring Without Acoustic Evidence:** The system must never assign a Pronunciation score based on text transcripts alone. If raw audio or phoneme-level acoustic data is missing or corrupted, the UI must display **"Insufficient Acoustic Data"**.
2. **Contextual Sentence Analysis:** The AI engine is prohibited from flagging isolated words as errors without evaluating the surrounding conversational context.
3. **Accent Fairness & Inclusivity:** The system must celebrate regional linguistic diversity. A speaker's native accent (e.g., Indian, Spanish, Japanese, German, Nigerian) must **never** be penalized if their pronunciation is clear, intelligible, and comprehensible.
4. **Confidence-Gated Attribution:** When speaker diarization confidence falls below 75%, speech segments must be labeled as `Unknown Speaker` rather than erroneously attributing words to another meeting participant.
5. **Mandatory Participant Consent:** Audio capture cannot begin silently. The user is required to confirm that all participants have been notified and have consented to session analysis.

