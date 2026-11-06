# Password Recovery and Change Workflow

## 1. Forgot Password Flow
1. User submits email address via `POST /api/v1/auth/forgot-password`.
2. Response is always generic: *"If this email is registered, password reset instructions have been sent."* This eliminates email enumeration attacks.
3. If the user exists and is active:
   - A 32-byte cryptographic token is generated.
   - The SHA-256 hash is saved to `password_reset_tokens` with a 30-minute expiration.
   - An email with a secure link is dispatched.

## 2. Password Reset
1. User navigates to the reset page and submits the token with new password via `POST /api/v1/auth/reset-password`.
2. Token hash and expiration are verified.
3. Password is updated with Bcrypt / Argon2id hashing.
4. **Security Invalidation:** All existing user sessions across all devices are immediately revoked.
5. Confirmation email is dispatched and an audit log event is recorded.

## 3. Password Change
1. Authenticated user submits `current_password` and `new_password` via `POST /api/v1/auth/change-password`.
2. Current password hash is verified.
3. New password is saved and all other sessions (except the current active session) are revoked.

