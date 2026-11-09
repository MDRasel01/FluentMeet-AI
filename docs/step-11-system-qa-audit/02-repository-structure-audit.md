# Step 11: 02 — Repository Structure & File Organization Audit

**Module:** Repository Structure Audit  
**Step:** 11 of 12  
**Repository:** FluentMeet AI Monorepo  

---

## 1. Directory Tree & Monorepo Boundaries

```
FluentMeet-AI/
├── apps/
│   ├── admin/                # Internal administrative portal
│   ├── dashboard/            # Next.js 14 Web Dashboard (Tailwind CSS, React 18)
│   │   ├── src/features/reports/ # Step 10 & 11 UI components (Summary, Detail, Trends)
│   │   └── DashboardApp.tsx  # Interactive multi-view dashboard application
│   └── extension/            # Chrome Extension MV3
│       ├── src/background/   # Service Worker & Session FSM Controller
│       ├── src/offscreen/    # Offscreen Audio Capture & AudioWorklet PCM Processor
│       ├── src/platforms/    # Google Meet, MS Teams, Zoom Web platform adapters
│       └── tests/unit/       # 18 passing Vitest unit tests
├── packages/
│   ├── api-client/           # Shared TypeScript REST/WSS client SDK
│   ├── shared-constants/     # Shared status codes, error codes, limits
│   └── shared-types/         # Protocol, audio, report TypeScript interfaces
├── services/
│   ├── api/                  # Python 3.14 FastAPI Backend Application
│   │   ├── app/
│   │   │   ├── analysis/     # Step 08: Linguistic analysis & Gemini 2.5 Flash client
│   │   │   ├── api/v1/       # 10 RESTful routers (auth, meetings, audio, reports, etc.)
│   │   │   ├── audio/        # Step 06: Binary audio ingestion, buffering, storage
│   │   │   ├── core/         # Config, DB engine, Redis pool, security crypto
│   │   │   ├── models/       # 19 SQLAlchemy 2.0 Async PostgreSQL models
│   │   │   ├── pronunciation/# Step 09: Acoustic prosody, phoneme alignment, IELTS
│   │   │   ├── reports/      # Step 10: Validation, builder, history, analytics, export
│   │   │   ├── schemas/      # Pydantic v2 request/response schemas
│   │   │   ├── transcription/# Step 07: Faster-Whisper, Pyannote, Silero VAD
│   │   │   └── websocket/    # WSS audio streaming endpoint & connection manager
│   │   ├── migrations/       # Alembic migrations (versions 001 to 006)
│   │   └── tests/            # 157 passing Pytest API unit, security & integration tests
│   └── worker/               # Background Asynchronous Workers (Celery & Redis Streams)
│       ├── app/consumers/    # audio, transcription, analysis, pronunciation, report
│       └── tests/            # 20 passing Pytest worker tests
├── scripts/                  # Standalone verification and automated Chrome test scripts
│   ├── verify_step08_analysis.py
│   ├── verify_step09_pronunciation.py
│   ├── verify_step10_report_engine.py
│   ├── verify_step11_system_qa_audit.py
│   └── test_chrome_system_audit.py
└── docs/                     # Step 01 to Step 11 Technical Specifications & QA Audits
```

---

## 2. Structural Integrity & Artifact Retention Check

- **No circular file references**: Python modules adhere strictly to top-down dependency flow (`main.py` $\to$ `api/v1` $\to$ `services` $\to$ `models`).
- **No stray temporary directories**: `.pytest_cache`, `dist`, and `build` directories are properly ignored in `.gitignore`.
- **Zero duplicate source of truth**: Models in `services/api/app/models/` serve as the single authority for database schema, with Alembic migrations tracking revisions incrementally.

