# API & WebSocket Foundation — FluentMeet AI

## REST API V1 Endpoints
- `GET /health/live`: Liveness probe for orchestrators (Kubernetes/ECS).
- `GET /health/ready`: Readiness probe verifying PostgreSQL & Redis connectivity.
- `POST /api/v1/auth/register`: Create user account and organization membership.
- `POST /api/v1/auth/login`: Issue short-lived access JWT (15m) and rotating refresh JWT (7d).
- `POST /api/v1/auth/refresh`: Refresh access tokens securely.
- `GET /api/v1/users/me`: Fetch authenticated profile and preferences.
- `PUT /api/v1/users/me`: Update profile data.
- `GET /api/v1/meetings`: Paginated list of user meeting sessions.
- `POST /api/v1/meetings`: Initialize meeting session with participant consent logging.
- `GET /api/v1/meetings/{id}`: Retrieve meeting details and performance metrics.
- `PATCH /api/v1/meetings/{id}/end`: Cleanly finalize meeting duration and trigger analysis.

## Authenticated WebSocket Protocol
- Route: `/ws/v1/sessions/{session_id}?token={jwt_token}`
- Supported events:
  - `connection_ack`: Server handshake acknowledgement
  - `ping` / `pong`: Heartbeat keeping connection open through NAT/proxies
  - `broadcast_event`: Multi-party notification within meeting session
  - `ack`: Message acknowledgement

