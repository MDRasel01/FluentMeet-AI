# Email Verification System

## 1. Verification Security Rules
- Cryptographically secure token generated using `secrets.token_urlsafe(32)`.
- Only the SHA-256 hash of the token is persisted in `email_verification_tokens`.
- Expiration window: exactly 30 minutes from issuance.
- Strict single-use policy: marked with `used_at` timestamp immediately upon successful verification.
- Account enumeration protection: `resend-verification` endpoint always returns a generic success response regardless of whether the email exists.

## 2. API Endpoints
- `POST /api/v1/auth/verify-email`:
  - Request: `{"token": "raw-opaque-token"}`
  - Effect: Updates `users.is_verified = True`, `users.status = "active"`, and records `email_verified_at`.
- `POST /api/v1/auth/resend-verification`:
  - Request: `{"email": "user@example.com"}`
  - Effect: Generates a new 30-minute token and dispatches email.

