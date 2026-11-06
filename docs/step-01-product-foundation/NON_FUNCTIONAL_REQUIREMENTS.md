# Non-Functional Requirements Specification (NFR)

**Product Name:** AI Meeting English Coach  
**Document ID:** SPEC-NFR-V1.0  
**Status:** Approved Quality & Reliability Baseline  
**Version:** 1.0.0  

---

## 1. Traceable Quality Requirements Index

| ID | Category | Requirement Summary | SLA / Target Metric |
|---|---|---|---|
| **NFR-001** | Performance | Extension UI Initial Render | < 250ms cold start, < 50ms warm |
| **NFR-002** | Performance | Audio Streaming Chunk Latency | < 500ms transmission to Redis |
| **NFR-003** | Performance | Post-Meeting Report Turnaround | < 3x meeting duration (e.g., < 9m for 30m call) |
| **NFR-004** | Performance | Web Dashboard Core Web Vitals | LCP < 1.5s, FID < 50ms, CLS < 0.05 |
| **NFR-005** | Scalability | Concurrent Audio Streaming Sessions | 10,000 concurrent sessions at peak |
| **NFR-006** | Scalability | Horizontal Worker Scaling | Dynamic autoscaling based on queue depth |
| **NFR-007** | Scalability | Database Query Latency | p95 < 50ms for dashboard queries |
| **NFR-008** | Security | Transport Encryption | TLS 1.3 mandatory for all HTTPS & WSS |
| **NFR-009** | Security | Media Encryption at Rest | AES-256-GCM for S3 audio objects |
| **NFR-010** | Security | Session Token Lifecycle | JWT Access (15m TTL), Refresh (7d rotating) |
| **NFR-011** | Security | Content Security Policy (CSP) | Strict CSP v3, no `unsafe-eval` in extension |
| **NFR-012** | Reliability | WebSocket Disconnect Recovery | Exponential backoff reconnect (max 60s buffer) |
| **NFR-013** | Reliability | Worker Job Idempotency | Safe at-least-once task execution |
| **NFR-014** | Reliability | Pipeline Availability | 99.9% uptime for core API and ingestion |
| **NFR-015** | Accessibility| WCAG 2.1 AA Compliance | 100% compliant across Web Dashboard & Extension |
| **NFR-016** | Accessibility| Keyboard Navigation | 100% interactive elements keyboard accessible |
| **NFR-017** | Privacy | Mandatory Recording Consent | Verifiable audit log prior to audio capture |
| **NFR-018** | Privacy | Ephemeral Data Retention | Automated cryptographic purging (7/30/90 days)|
| **NFR-019** | Privacy | Multi-Tenant Data Isolation | Logical tenant separation with zero cross-leakage |
| **NFR-020** | AI Ethics | Zero Acoustic Hallucination | Pronunciation scoring forbidden without audio |
| **NFR-021** | AI Ethics | Accent Fairness & Neutrality | Regional accents never penalized as grammar |
| **NFR-022** | AI Ethics | Evidence-Backed Linguistic Claims | Exact transcript quote & timestamp required |
| **NFR-023** | AI Ethics | Insufficient Data Handling | Display "Insufficient Evidence" when speech < 2m |
| **NFR-024** | Compliance | GDPR / CCPA Compliance | Right to be forgotten & data export within 72h |

---

## 2. Granular Non-Functional Specifications

### 2.1 Performance & Latency (NFR-001 – NFR-004)
- **Audio Chunking:** Offscreen document must slice audio into 1-second chunks (16kHz 16-bit PCM = 32,000 bytes/sec) with minimal CPU usage (< 3% CPU overhead on modern 4-core laptops).
- **Report Generation SLA:** A 30-minute meeting must complete ASR, Diarization, and Gemini analysis within 9 minutes under standard queue load.
- **Audio Player Seeking:** Audio scrubbing must seek and resume playback within 150ms of user input.

### 2.2 Scalability & Elastic Concurrency (NFR-005 – NFR-007)
- **Streaming Ingestion Gateway:** WebSocket endpoints built with async FastAPI / Uvicorn must support non-blocking I/O capable of handling 10,000 simultaneous audio streams partitioned across Redis Stream clusters.
- **Worker Autoscaling:** The Celery/worker infrastructure must autoscale based on queue backlog length; if queue wait time exceeds 2 minutes, new worker containers spin up dynamically.

### 2.3 Security & Cryptography (NFR-008 – NFR-011)
- **Token Security:** Authentication tokens in the extension are stored in `chrome.storage.local` (isolated to extension sandbox). Web Dashboard utilizes `HttpOnly`, `SameSite=Strict`, `Secure` cookies.
- **API Defense:** Rate limiting enforced via Redis token bucket algorithm (100 req/min for general endpoints; 5 req/min for authentication).

### 2.4 Reliability, Fault Tolerance & Recovery (NFR-012 – NFR-014)
- **Local Chunk Buffering:** When a network disconnect occurs during a meeting, the extension offscreen document buffers audio chunks in client IndexedDB storage (up to 60MB / 30 minutes of compressed audio) and flushes them sequentially upon reconnection.
- **Worker Resilience:** Processing workers use Celery `acks_late=True`. If an AWS instance terminates mid-job, the task is redelivered without audio corruption.

### 2.5 Accessibility Standards (NFR-015 – NFR-016)
- **Contrast:** Regular text maintains minimum 4.5:1 contrast against light and dark surfaces. Headings maintain 3:1.
- **Focus Indicators:** Interactive buttons and transcript segments feature high-contrast 2px offset focus rings.

### 2.6 Privacy, AI Ethics & Regulatory Compliance (NFR-017 – NFR-024)
- **Strict Anti-Bias Policy:** Regional accents (e.g., Indian, Spanish, Japanese, French, Nigerian) must not be penalized. AI prompts explicitly instruct Google Gemini to evaluate grammatical syntax and semantic clarity, never penalizing dialectical word order unless communication fails.
- **Evidence Mandate:** Every identified error must link to:
  1. Spoken Transcript Excerpt.
  2. Start and End Timestamp.
  3. Grammatical Rule or Pragmatic Justification.
- **Insufficient Evidence Gate:** If a speaker speaks for less than 120 seconds in a meeting, the system refuses to output a generalized English Score, showing instead: *"Insufficient speaking duration to compute an accurate score (Spoke 45s; minimum required: 120s)."*

