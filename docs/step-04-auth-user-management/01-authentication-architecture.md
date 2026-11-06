# Authentication Architecture — FluentMeet AI

## 1. Overview
FluentMeet AI utilizes a dual-tier identity and authorization architecture designed for multi-tenant SaaS workloads:
1. **Platform Identity:** Top-level user identity with credentials, email verification status, and global platform roles (`individual`, `super_admin`, `support_admin`, `platform_analyst`).
2. **Organization Context:** Membership in one or more enterprise organizations with granular tenant-level roles (`owner`, `admin`, `manager`, `member`) and server-side RBAC enforcement.

## 2. High-Level Security Architecture
```
[Client (Web / Extension)]
         │
         ▼ (HTTPS Bearer Token)
[FastAPI Authentication Middleware]
         │ (Decodes Access JWT, checks claims: sub, sid, exp, iss, aud)
         ▼
[Active Session & Revocation Check]
         │ (Queries auth_sessions in DB / Redis)
         ▼
[Tenant-Scoped Authorization Layer]
         │ (Verifies Organization Membership & RBAC Permission Matrix)
         ▼
[Database / Resource Access]
```

## 3. Key Security Properties
- **Zero-Trust Client Identity:** Organization IDs and roles provided in client payloads are never trusted without server-side verification against `organization_members`.
- **Short-Lived Access Tokens:** 15-minute expiration minimizes exposure windows.
- **Stateful Rotating Refresh Tokens:** Stored as cryptographic hashes with family tracking; reuse triggers immediate revocation of the entire token family.
- **Cryptographic Separation:** Passwords hashed with Bcrypt (Argon2id compatible); one-time tokens generated via `secrets.token_urlsafe(32)` and persisted exclusively as SHA-256 hashes.

