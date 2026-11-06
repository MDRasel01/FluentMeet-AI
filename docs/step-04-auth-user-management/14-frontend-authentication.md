# Frontend Authentication & Dashboard Integration

## 1. Web Dashboard Client Integration
The Web Dashboard (`apps/dashboard/`) consumes backend authentication and organization endpoints through the unified `@fluentmeet/api-client` package.

### Client Authentication Flow
1. **Login:** Authenticates credentials via `POST /api/v1/auth/login`. Receives 15-minute JWT access token and 7-day refresh token.
2. **Token Storage:**
   - In production web contexts, refresh tokens are stored in `HttpOnly`, `Secure`, `SameSite=Lax` cookies to defend against XSS.
   - Access tokens are maintained in client memory.
3. **Auto-Refresh:**
   - Upon encountering a 401 response or near access token expiration, `@fluentmeet/api-client` invokes `refreshTokens()` to maintain seamless user sessions without interrupts.

## 2. Integrated Screens
- Sign Up with password confirmation and terms acceptance
- Sign In with validation and account status error handling
- Email Verification status and resend link
- Forgot Password & Reset Password forms
- Organization Switcher and Organization Creation modal
- Team Members management with role assignment and removal
- User Profile Settings, Security Settings, and Active Session listing
