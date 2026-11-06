# Functional Requirements Specification (FRD)

**Product Name:** AI Meeting English Coach  
**Document ID:** SPEC-FRD-V1.0  
**Status:** Approved Functional Requirements Baseline  
**Version:** 1.0.0  

---

## 1. Requirement Traceability Index (FR-001 to FR-028)

| ID | Requirement Title | Target Interface | Core Modules Involved | Priority (MVP) |
|---|---|---|---|:---:|
| **FR-001** | User Registration | Web Dashboard | FastAPI, Postgres, Auth Service | MUST |
| **FR-002** | User Authentication & Session | Web / Extension | JWT Token Handler, Redis Cache | MUST |
| **FR-003** | Multi-Tenant Organization Management | Web Dashboard | Organization Service, Postgres | MUST |
| **FR-004** | Role-Based Access Control (RBAC) | All Interfaces | Auth Middleware, Database Scopes | MUST |
| **FR-005** | Chrome Extension Authentication | Chrome Extension | Side Panel, Service Worker, OAuth | MUST |
| **FR-006** | Browser Meeting URL & DOM Detection | Chrome Extension | Content Script, MutationObserver | MUST |
| **FR-007** | Meeting Platform Adapter Detection | Chrome Extension | Platform Adapter Registry | MUST |
| **FR-008** | Meeting Participant Discovery | Chrome Extension | DOM Scrapers (Meet/Zoom/Teams) | MUST |
| **FR-009** | Mandatory Participant Consent Verification| Chrome Extension | Side Panel UI, Audit Logger | MUST |
| **FR-010** | Dual-Stream Audio Capture | Chrome Extension | Offscreen Doc (tabCapture + Mic) | MUST |
| **FR-011** | Real-time Binary Audio Streaming | Chrome Extension | WebSocket Client, Redis Stream Ingest| MUST |
| **FR-012** | Speech-to-Text (ASR) Processing | Backend Workers | ASR Engine, Audio Stitcher | MUST |
| **FR-013** | Speaker Diarization | Backend Workers | Acoustic Diarization Pipeline | MUST |
| **FR-014** | Speaker-to-Participant Identity Mapping | Backend Workers | Alignment Service, Match Scorer | MUST |
| **FR-015** | Interactive Transcript Generation | Web Dashboard | Transcript Service, Audio Sync Player| MUST |
| **FR-016** | Grammar & Syntactic Error Analysis | Backend Workers | Gemini AI Language Engine | MUST |
| **FR-017** | Vocabulary & Lexical Precision Analysis | Backend Workers | Gemini AI Language Engine | MUST |
| **FR-018** | Fluency & Speech Dynamics Analysis | Backend Workers | Audio Metrics + Gemini AI Engine | MUST |
| **FR-019** | Pronunciation & Articulatory Evaluation | Backend Workers | Acoustic Evaluation Engine | SHOULD (v1.1)|
| **FR-020** | Individual Meeting Report Generation | Web Dashboard | Report Engine, Postgres, S3 | MUST |
| **FR-021** | Meeting History, Search & Filtering | Web Dashboard | Meeting Archive API, Postgres | MUST |
| **FR-022** | Longitudinal Performance Tracking | Web Dashboard | Analytics Service, Recharts Engine | SHOULD (v1.1)|
| **FR-023** | Contextual Learning Recommendations | Web Dashboard | Gemini Practice Drill Generator | SHOULD (v1.1)|
| **FR-024** | Scoped Team Communication Analytics | Web Dashboard | Aggregation Service (Role Gated) | SHOULD (v1.1)|
| **FR-025** | Multi-Dimensional Usage & Billing Engine | Web Dashboard | Stripe Billing, Metering Service | MUST |
| **FR-026** | Super Admin Platform Operations | Admin Panel | Admin Service, System Telemetry | MUST |
| **FR-027** | Multi-Format Data Export | Web Dashboard | PDF/JSON Exporter, S3 Presigner | SHOULD (v1.1)|
| **FR-028** | Granular Retention & Data Erasure | All Interfaces | Purge Worker, S3/DB Janitor (GDPR) | MUST |

---

## 2. Granular Specification for FR-001 through FR-028

### FR-001: User Registration
- **Description:** Allows new individual users or team invitees to register using an email address, password, full name, and native language profile.
- **Inputs:** `email`, `password` (min 8 chars, 1 uppercase, 1 symbol), `full_name`, `native_language`.
- **Processing Rules:** Hashes password with bcrypt/Argon2. Validates email uniqueness. Sends cryptographic email verification token (TTL: 24h).
- **Outputs:** Verification email sent; user created with `status: pending_verification`.

### FR-002: User Authentication & Session Management
- **Description:** Authenticates users via credentials or SSO, issuing short-lived JWT access tokens (15 mins) and rotating refresh tokens (7 days).
- **Processing Rules:** Rate-limited to 5 failed attempts per 10 minutes per IP. Sessions revocable in Redis.

### FR-003: Multi-Tenant Organization Management
- **Description:** Supports isolated organization tenants. Admins can manage teams, invite members via email, and assign department tags.
- **Processing Rules:** Enforces unique tenant domains and limits active seats to subscribed plan capacity.

### FR-004: Role-Based Access Control (RBAC)
- **Description:** Enforces permission boundaries across Individual, Team Member, Team Manager, Org Admin, and Super Admin roles.
- **Processing Rules:** SQL-level data scoping via tenant ID and role checks on all protected API routes.

### FR-005: Chrome Extension Authentication
- **Description:** Securely syncs authentication state between the browser web session and the Chrome Extension storage (`chrome.storage.local`).
- **Processing Rules:** Uses secure messaging handoff or 6-digit pairing code fallback.

### FR-006: Browser Meeting URL & DOM Detection
- **Description:** Content script observes active browser tabs to detect supported meeting sessions (`meet.google.com/*`, etc.).
- **Processing Rules:** Detects in-call DOM states (e.g., active call toolbar, participant grid) to prevent false positives in meeting lobby screens.

### FR-007: Meeting Platform Adapter Detection
- **Description:** Identifies the specific platform and loads the corresponding DOM adapter (MeetAdapter, ZoomAdapter, TeamsAdapter).

### FR-008: Meeting Participant Discovery
- **Description:** Scrapes participant display names and muted/speaking DOM indicators during an active call.
- **Processing Rules:** Runs mutation observers on participant panels; updates participant roster without degrading browser performance.

### FR-009: Mandatory Participant Consent Verification
- **Description:** Enforces explicit user confirmation that all participants consent to AI audio analysis before recording begins.
- **Processing Rules:** The "Start Analysis" button remains strictly disabled until the consent checkbox is checked. Records consent timestamp in the audit database.

### FR-010: Dual-Stream Audio Capture
- **Description:** Captures two isolated audio streams via offscreen document: remote participants' audio via `chrome.tabCapture` and local user audio via `getUserMedia`.
- **Processing Rules:** Formats streams to 16kHz, 16-bit mono PCM.

### FR-011: Real-time Binary Audio Streaming
- **Description:** Transmits chunked binary audio (1-second intervals) to backend ingestion gateway via secure WebSocket.
- **Processing Rules:** Chunks include sequence headers and millisecond timestamps. Local IndexedDB buffering absorbs network drops.

### FR-012: Speech-to-Text (ASR) Processing
- **Description:** Transcribes audio chunks into text with millisecond-level word start/end timestamps and punctuation.

### FR-013: Speaker Diarization
- **Description:** Clusters audio segments into distinct acoustic voices (`Speaker A`, `Speaker B`) across the timeline.

### FR-014: Speaker-to-Participant Identity Mapping
- **Description:** Correlates diarized acoustic voice clusters with scraped DOM participant identities using local microphone tracking and speaking indicators.
- **Processing Rules:** When confidence score < 75%, maps segment to `Unknown Speaker`.

### FR-015: Interactive Transcript Generation
- **Description:** Produces an interactive transcript viewable on Web Dashboard where clicking text immediately seeks audio to that timestamp.

### FR-016: Grammar & Syntactic Error Analysis
- **Description:** Analyzes speaker utterances using Google Gemini API to identify grammatical blunders, tense mismatches, and preposition mistakes.
- **Processing Rules:** Must output structured JSON containing the original sentence, exact error span, correction, explanation, and severity.

### FR-017: Vocabulary & Lexical Precision Analysis
- **Description:** Evaluates spoken vocabulary range, detects overused repetitive words, and recommends executive business phrasing.

### FR-018: Fluency & Speech Dynamics Analysis
- **Description:** Computes Words Per Minute (WPM), pause durations, and filler word frequency ("um", "uh", "you know").

### FR-019: Pronunciation & Articulatory Evaluation
- **Description:** Evaluates phoneme articulation and word stress.
- **Processing Rules:** Strictly requires acoustic audio data; transcript-only scoring is forbidden. Displays IPA phonetic guide.

### FR-020: Individual Meeting Report Generation
- **Description:** Compiles all linguistic analyses into a comprehensive post-meeting report for each analyzed speaker.

### FR-021: Meeting History, Search & Filtering
- **Description:** Archive interface allowing users to search, filter by platform/date, and inspect past meetings.

### FR-022: Longitudinal Performance Tracking
- **Description:** Aggregates multi-week trends across Grammar, Vocabulary, Fluency, and Pronunciation.

### FR-023: Contextual Learning Recommendations
- **Description:** Dynamically generates 3-minute interactive daily practice drills derived directly from real meeting mistakes.

### FR-024: Scoped Team Communication Analytics
- **Description:** Generates aggregate team communication metrics for Team Managers while strictly preserving individual participant privacy.

### FR-025: Multi-Dimensional Usage & Billing Engine
- **Description:** Meters meeting minutes, audio processing compute, and AI tokens; manages subscriptions via Stripe.

### FR-026: Super Admin Platform Operations
- **Description:** Provides internal platform visibility into tenant quotas, AI token expenses, worker queues, and error streams.

### FR-027: Multi-Format Data Export
- **Description:** Allows users to export meeting transcripts and coaching reports in PDF and JSON formats.

### FR-028: Granular Retention & Data Erasure
- **Description:** Implements automated data purging according to organization retention policies (7, 30, 90 days) and supports complete GDPR "Right to be Forgotten" account erasure.

