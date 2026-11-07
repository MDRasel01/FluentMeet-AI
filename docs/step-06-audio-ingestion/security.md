# Security, Multi-Tenancy & Data Protection

## 1. Authentication & WebSocket Origin Validation

### 1. Handshake Origin Validation
All WebSocket connections pass through `validate_origin()` before being accepted:
* Connections originating from unauthorized origins are immediately closed with `1008 Policy Violation`.
* Permitted origins include:
  * `http://localhost:3000` & `http://127.0.0.1:3000` (Local Next.js dashboard)
  * `http://localhost:5173` (Vite dev server)
  * `chrome-extension://*` (Authorized Chrome Extension IDs)

### 2. JWT Cryptographic Verification
* Every WebSocket connection requires a valid `token` query parameter.
* Token signature is checked against `settings.JWT_SECRET_KEY` using `HS256`.
* User identity (`sub`) and tenant (`org_id`) are extracted from token claims.
* Expired or forged tokens cause immediate `1008 Policy Violation` termination.

---

## 2. Multi-Tenant Audio Isolation

* **Database Layer:** All queries filtering audio streams, segments, gaps, and metrics enforce `organization_id` or `user_id` ownership constraints.
* **Storage Layer:** Object storage keys strictly enforce the prefix `organizations/{org_id}/...`. A compromised client cannot read or overwrite segments belonging to other organizations.
* **Stream Bus Layer:** Redis events include `organization_id` to allow tenant-aware worker dispatching and rate-limiting.

---

## 3. Tamper Protection & Checksums

* Every audio segment written to storage includes a calculated SHA-256 digest in its database record.
* Before any background worker or downstream Step 07 AI model processes a segment, it recalculates the SHA-256 hash. If any byte was altered or corrupted, processing halts immediately and an audit alert is triggered.
