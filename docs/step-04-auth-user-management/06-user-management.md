# User Management and Profile Settings

## 1. Profile Data Structure
Every user record in `users` has an attached `user_profiles` record containing:
- `avatar_url`: User avatar image URL
- `phone_number`: Optional contact number
- `bio`: Professional bio
- `job_title`: Current role (e.g., Engineering Lead, Product Manager)
- `english_learning_goal`: Key focus area (e.g., Executive Presentations, Technical Negotiation)
- `target_speaking_score`: Benchmark fluency score (default: 80)

## 2. Profile Management Endpoints
- `GET /api/v1/users/me`: Returns complete user identity and profile metadata.
- `PATCH /api/v1/users/me`: Updates profile and preference fields.
- `PATCH /api/v1/users/me/email`: Requests email change with password re-authentication.

## 3. Account Deactivation
- **Endpoint:** `DELETE /api/v1/users/me`
- **Safety Guards:**
  - Password re-authentication is mandatory.
  - **Sole Owner Protection:** If the user is the only Owner of an active organization, deactivation is blocked with an explicit error requiring them to transfer ownership or delete the organization first.
  - Upon deactivation, all active sessions are revoked, `status` becomes `"deactivated"`, `is_active = False`, and an audit event is logged.
