# Architecture Overview — FluentMeet AI Infrastructure

## 1. Monorepo Topology
FluentMeet AI operates as a unified enterprise monorepo orchestrated via `pnpm` workspaces for TypeScript applications and `uv`/`pip` for Python backend microservices.

```
fluentmeet-ai/
├── apps/
│   ├── dashboard/       # Next.js 14 App Router Web Client
│   ├── extension/       # Manifest V3 Chrome Extension (Sidepanel + Audio Capture)
│   └── admin/           # Superadmin & Tenant Management Portal
├── packages/
│   ├── shared-types/    # TypeScript interfaces across all clients
│   ├── shared-constants/# Platform constants, error codes, limits
│   └── api-client/      # Isomorphic HTTP & WebSocket API client
├── services/
│   ├── api/             # FastAPI REST & WebSocket Backend Service
│   └── worker/          # Celery Distributed Task Processing Worker
├── infra/               # Nginx reverse proxy and deployment configs
└── docker-compose.yml   # Multi-service local orchestrator
```

## 2. Communication Protocols
- **Client to API:** HTTPS REST for Auth, Profiles, Meetings, Billing.
- **Real-Time Coaching:** WSS (WebSocket) at `/ws/v1/sessions/{session_id}` with JWT authentication and bi-directional JSON streaming.
- **Async Processing:** Redis 7 Pub/Sub broker with Celery workers for long-running audio processing and report generation.
