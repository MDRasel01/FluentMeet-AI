# Product Architecture & Engineering Specification

**Product Name:** AI Meeting English Coach  
**Document ID:** ARCH-V1.0-CORE  
**Status:** Approved Architectural Blueprint  
**Version:** 1.0.0  

---

## 1. High-Level Architectural Overview

The AI Meeting English Coach system is designed as a high-throughput, fault-tolerant, multi-tenant SaaS platform. It combines real-time client-side media capture within a Google Chrome Extension, low-latency binary audio streaming via WebSockets, an asynchronous worker processing pipeline, and Google Gemini AI language analysis.

```mermaid
flowchart TD
    subgraph ClientLayer["Client Layer (Browser & Extension)"]
        MeetTab["Active Meeting Tab (Meet/Zoom/Teams)"]
        ContentScript["Content Script (DOM Participant Scraper)"]
        OffscreenDoc["Offscreen Document (Audio Mixer: Tab + Mic)"]
        SidePanel["Chrome Side Panel UI (React / Tailwind)"]
        WebDashboard["Web Dashboard (Next.js / TypeScript)"]
        AdminDashboard["Admin Console (Super Admin / Org Admin)"]
    end

    subgraph GatewayLayer["Ingestion & API Gateway"]
        NginxLB["Load Balancer & TLS 1.3 Termination"]
        FastAPI_Core["FastAPI Core (REST API / JWT RBAC)"]
        WS_Ingest["WebSocket Audio Ingestion Gateway"]
    end

    subgraph QueueStorage["Buffering & Queue Layer"]
        RedisAudioBuf["Redis Stream (Audio Chunk Buffer)"]
        RedisQueue["Redis / Celery Task Queue (Jobs)"]
    end

    subgraph ProcessingPipeline["Asynchronous Processing Pipeline"]
        WorkerPool["Worker Nodes (Python / Celery)"]
        AudioStitcher["Audio Splicer & VAD Normalizer"]
        ASREngine["Speech-to-Text Engine (ASR)"]
        DiarizeEngine["Speaker Diarization Engine"]
        Matcher["Participant-to-Speaker Alignment"]
        GeminiEngine["Gemini AI Language Analysis Engine"]
        PronounceEngine["Acoustic Pronunciation Evaluator"]
    end

    subgraph PersistenceLayer["Multi-Tenant Persistence Layer"]
        PostgresDB[("PostgreSQL (Multi-Tenant Relational Data)")]
        ObjectStorage[("S3-Compatible Object Store (Audio Chunks)")]
        RedisCache[("Redis Cache (Sessions & State)")]
    end

    MeetTab --> ContentScript
    MeetTab --> OffscreenDoc
    ContentScript --> SidePanel
    OffscreenDoc --> WS_Ingest
    SidePanel --> FastAPI_Core

    WebDashboard --> FastAPI_Core
    AdminDashboard --> FastAPI_Core

    WS_Ingest --> RedisAudioBuf
    FastAPI_Core --> RedisQueue

    RedisAudioBuf --> WorkerPool
    RedisQueue --> WorkerPool

    WorkerPool --> AudioStitcher
    AudioStitcher --> ASREngine
    AudioStitcher --> DiarizeEngine
    ASREngine --> Matcher
    DiarizeEngine --> Matcher
    Matcher --> GeminiEngine
    AudioStitcher --> PronounceEngine

    GeminiEngine --> PostgresDB
    PronounceEngine --> PostgresDB
    WorkerPool --> ObjectStorage
    FastAPI_Core --> PostgresDB
    FastAPI_Core --> RedisCache
```

---

## 2. Core Subsystems & Component Responsibilities

### 2.1 Chrome Extension Subsystem (Manifest V3)
Due to Manifest V3 service worker lifecycle constraints, the extension separates concerns across four distinct execution contexts:

1. **Background Service Worker (`service_worker.ts`):**  
   Manages extension lifecycle, authenticates against backend APIs, maintains user session tokens, coordinates between tabs, and monitors meeting tab state transitions.
2. **Content Script (`content_script.ts`):**  
   Injected into supported meeting domains (`meet.google.com`, `zoom.us`, `teams.microsoft.com`). Observes DOM mutations to detect active call status, scrapes participant names and avatar states, and listens for meeting termination events.
3. **Offscreen Document (`offscreen.html` / `offscreen.ts`):**  
   Required by Chrome Manifest V3 to execute continuous media APIs. Captures:
   - System/Tab incoming audio via `chrome.tabCapture.getMediaStreamId()`.
   - Local user microphone audio via `navigator.mediaDevices.getUserMedia()`.
   - Synchronizes, resamples, encodes into 16kHz 16-bit Mono Linear PCM or Opus chunks, and streams them over a persistent secure WebSocket connection.
4. **Side Panel UI (`sidepanel.tsx`):**  
   Provides the user with non-obtrusive controls: Meeting detection confirmation, Consent assertion, Recording Pause/Resume/Stop, live audio level meters, and one-click navigation to full web reports.

---

### 2.2 Web Dashboard Subsystem (Next.js & React)
Built with **Next.js (App Router)**, **TypeScript**, and **Tailwind CSS**:
- **Authentication & Tenant Context:** Handles enterprise SSO, email/password JWT authentication, and organization switching.
- **Interactive Transcript & Audio Player:** Synchronizes audio playback with text segments. Clicking any sentence immediately seeks the audio player to that exact millisecond.
- **English Analytics Engine:** Visualizes Grammar mistakes, Vocabulary upgrades, Fluency metrics (WPM, pause histograms, filler density), and Pronunciation breakdowns using responsive SVG charts.
- **Micro-Learning Center:** Dynamically converts meeting mistakes into personalized 3-minute daily practice challenges.

---

### 2.3 Super Admin & Enterprise Admin Console
Provides operational observability and multi-tenant management:
- **Tenant Administration:** Organization provisioning, seat limits, plan downgrades/upgrades, and billing cycles.
- **Usage & Cost Metering:** Real-time tracking of ingested meeting minutes, ASR computation time, and Gemini API token consumption.
- **System Health:** Live queue backlog monitoring, worker node throughput, and error rates.

---

### 2.4 Backend Core Subsystem (FastAPI & Python)
A high-concurrency asynchronous API service built with **Python 3.11+** and **FastAPI**:
- **RESTful Endpoints:** Serves meeting metadata, paginated transcripts, aggregated reports, user profiles, and organization billing data.
- **WebSocket Gateway (`/ws/audio-stream/{session_id}`):** High-speed ingestion of chunked binary audio. Validates sequence numbers, buffers chunks into Redis Streams, and detects network dropouts.
- **Security & RBAC Enforcement:** Validates JWT claims, organization tenant ID scoping, and enforces role-based access rules at the database query layer.

---

### 2.5 Audio Processing & AI Pipeline

```mermaid
sequenceDiagram
    autonumber
    participant Ext as Chrome Extension
    participant API as FastAPI Ingestion
    participant Worker as Audio & AI Worker
    participant ASR as ASR & Diarization
    participant Gemini as Google Gemini AI
    participant DB as Postgres & S3

    Ext->>API: Initialize Meeting Session (POST /sessions)
    API-->>Ext: Session ID & Secure WebSocket Token
    Ext->>API: Connect WebSocket (/ws/audio-stream/{session_id})
    loop During Meeting
        Ext->>API: Stream 1-sec PCM Audio Chunks + Timestamps
        API->>DB: Buffer chunks in S3 & Redis Stream
    end
    Ext->>API: Finalize Session (POST /sessions/{id}/complete)
    API->>Worker: Enqueue Processing Task (Job ID)
    Worker->>DB: Fetch & Stitch Stored Audio Chunks
    Worker->>ASR: Process Speech-to-Text & Speaker Diarization
    ASR-->>Worker: Segmented Transcripts with Speaker IDs & Timestamps
    Worker->>Worker: Map Diarized Speakers to Scraped Participant Names
    Worker->>Gemini: Send Structured Analysis Prompt (Full Context)
    Gemini-->>Worker: Structured JSON (Grammar, Vocab, Fluency, IELTS)
    Worker->>DB: Save Final Report, Transcript & Analytics
    Worker->>API: Notify Report Ready (WebSocket / Webhook)
    API-->>Ext: Status: Complete (View Report)
```

1. **Audio Assembly & Normalization:** Stitches incoming audio chunks, verifies chronological sequence numbers, and applies Voice Activity Detection (VAD) to trim silence.
2. **Speech-to-Text (ASR) & Diarization:** Transcribes speech into text with millisecond-precision word timestamps and groups utterances into speaker acoustic clusters.
3. **Speaker-to-Participant Identity Mapping:** Correlates acoustic voice activity with content-script scraped participant states (e.g., active speaking indicators, local microphone presence). Segments with low confidence remain attributed to `Unknown Speaker`.
4. **Google Gemini Language Analysis Engine:** Evaluates complete conversation context using Gemini 1.5/2.0 API with **Pydantic Structured Outputs**, extracting grammatical errors, professional rephrasing, lexical variety, and estimated IELTS band scores.
5. **Acoustic Pronunciation Evaluation:** Compares speech audio against target phoneme representations to surface objective articulation feedback without accent bias.

---

## 3. Multi-Tenancy & Data Isolation Model

To guarantee strict compliance with enterprise standards and data sovereignty:

1. **Logical Tenant Partitioning:**  
   Every database table contains an indexed `tenant_id` (foreign key to `organizations`). Every query executed by FastAPI is automatically filtered by the authenticated user's `tenant_id` via dependency injection and SQLAlchemy query scopes.
2. **Audio & Media Isolation:**  
   Audio files and raw transcripts are stored in Amazon S3/MinIO using structured bucket paths:  
   `s3://meeting-coach-media/{tenant_id}/{meeting_id}/raw_audio.wav`  
   Direct object access requires short-lived presigned URLs (TTL: 15 minutes) generated only for authorized session owners.
3. **Role-Based Redaction:**  
   Individual speaking scores are private to the speaker. Organization managers and team leads only have query access to aggregated, anonymized team-level metrics unless explicit peer-sharing permissions are configured.

---

## 4. Resilience, Reconnection & Fault Recovery

| Failure Scenario | Recovery Mechanism |
|---|---|
| **Transient WebSocket Drop** | The Chrome Extension buffers binary chunks locally in memory (up to 60 seconds). Upon reconnecting, chunks are flushed in strict chronological sequence. |
| **Worker Node Crash During AI Analysis** | Celery tasks use persistent message acknowledgement (`acks_late=True`). If a worker terminates, Redis redelivers the job to an active worker node with exponential backoff (max 3 retries). |
| **Side Panel Closed Accidentally** | Capture logic resides in the persistent Background Service Worker and Offscreen Document. Closing the side panel does not interrupt audio capture or WebSocket streaming. |
| **DOM Scraper Failure (Google Meet UI Update)** | If meeting participant selectors fail due to third-party DOM changes, audio capture and ASR continue uninterrupted. Unmatched speakers are assigned labeled aliases (`Speaker 1`, `Speaker 2`), and the admin is notified via telemetry. |

