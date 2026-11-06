# JWT and Session Management

## 1. Access Token Specifications
- **Format:** Signed JSON Web Token (JWT) using HS256 (or RS256 in enterprise SSO).
- **Lifetime:** 15 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES = 15`).
- **Standard Claims:**
  - `sub`: User UUID
  - `sid`: Auth Session UUID
  - `email`: User primary email address
  - `role`: Platform role (`individual`, `super_admin`, etc.)
  - `iss`: `fluentmeet-api`
  - `aud`: `fluentmeet-client`
  - `iat`: Issued at timestamp
  - `exp`: Expiration timestamp
  - `jti`: Unique token identifier UUID

## 2. Refresh Token Rotation & Reuse Detection
- **Mechanism:** Every call to `POST /api/v1/auth/refresh` invalidates the old refresh token by setting `used_at = now` and generates a newly rotated refresh token tied to the same `family_id`.
- **Token Reuse Attack Detection:** If a revoked or already-used refresh token is presented:
  1. The server identifies this as a potential credential theft.
  2. All refresh tokens in the entire `family_id` chain are immediately revoked.
  3. The associated `auth_sessions` record is marked `revoked_at = now`.
  4. Returns `401 Unauthorized` with a security violation alert.

## 3. Active Sessions Management
Users can view and manage their active sessions across devices:
- `GET /api/v1/auth/sessions`: Lists all active non-revoked sessions.
- `DELETE /api/v1/auth/sessions/{session_id}`: Revokes a specific device session.
- `POST /api/v1/auth/logout`: Revokes the current session.
- `POST /api/v1/auth/logout-all`: Atomically revokes all sessions for the user across all devices.

