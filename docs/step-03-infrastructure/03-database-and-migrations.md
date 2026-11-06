# Database Architecture & Migrations

## Database Engine
- **Primary:** PostgreSQL 16 (production & docker-compose)
- **Local Testing:** SQLite with `aiosqlite` in-memory engine for fast CI pipelines
- **ORM:** SQLAlchemy 2.0 with async engine and `async_sessionmaker`
- **Migrations:** Alembic with async migration support (`async_engine_from_config`)

## Relational Schema
1. `organizations`: Multi-tenant boundary, seat limits, retention policies.
2. `users`: Credentials, native language preferences, roles, verification status.
3. `organization_members`: Role-based membership linking users and organizations.
4. `subscriptions`: Plan tier, monthly quota minutes, renewal dates.
5. `meetings`: Session records, platform (Google Meet, Zoom, MS Teams), start/end times.
6. `meeting_participants`: Diarized participants, speaking time share.
7. `consent_records`: Explicit GDPR/compliance consent audit trail with timestamps and IP.
8. `usage_logs`: Metered minutes and AI token consumption.
9. `audit_logs`: Security and administrative actions.
