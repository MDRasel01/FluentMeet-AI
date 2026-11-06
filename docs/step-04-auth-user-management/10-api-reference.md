# API Reference — SaaS Authentication & Identity

All endpoints are versioned under the `/api/v1` prefix.

## 1. Authentication Endpoints
| Method | Path | Description | Auth Required |
|---|---|---|---|
| `POST` | `/auth/register` | Register new account (status: pending_verification) | No |
| `POST` | `/auth/verify-email` | Verify email with single-use token | No |
| `POST` | `/auth/resend-verification` | Resend verification email link | No |
| `POST` | `/auth/login` | Authenticate and issue JWT access & refresh tokens | No |
| `POST` | `/auth/refresh` | Rotate refresh token and issue new access token | No |
| `POST` | `/auth/logout` | Revoke current session and refresh tokens | Yes |
| `POST` | `/auth/logout-all` | Revoke all sessions across all devices | Yes |
| `POST` | `/auth/forgot-password` | Request password reset email | No |
| `POST` | `/auth/reset-password` | Set new password with reset token | No |
| `POST` | `/auth/change-password` | Update password with current password | Yes |
| `GET` | `/auth/sessions` | List all active sessions for current user | Yes |
| `DELETE` | `/auth/sessions/{id}` | Revoke a specific active session | Yes |

## 2. User Profile Endpoints
| Method | Path | Description | Auth Required |
|---|---|---|---|
| `GET` | `/users/me` | Fetch authenticated user profile and details | Yes |
| `PATCH` | `/users/me` | Update full name, timezone, bio, learning goals | Yes |
| `PATCH` | `/users/me/email` | Request email change with password check | Yes |
| `DELETE` | `/users/me` | Deactivate user account (password confirmed) | Yes |

## 3. Organization Endpoints
| Method | Path | Description | Auth Required |
|---|---|---|---|
| `POST` | `/organizations` | Create organization (caller becomes Owner) | Yes |
| `GET` | `/organizations` | List organizations the user belongs to | Yes |
| `GET` | `/organizations/{id}` | Retrieve organization details and settings | Yes |
| `PATCH` | `/organizations/{id}` | Update organization settings (Admin/Owner) | Yes |
| `DELETE` | `/organizations/{id}` | Delete organization (Owner only) | Yes |
| `GET` | `/organizations/{id}/members` | List members of organization | Yes |
| `PATCH` | `/organizations/{id}/members/{uid}` | Update member role | Yes |
| `DELETE` | `/organizations/{id}/members/{uid}` | Remove member from organization | Yes |
| `POST` | `/organizations/{id}/transfer-ownership` | Transfer ownership to member | Yes |

## 4. Invitation Endpoints
| Method | Path | Description | Auth Required |
|---|---|---|---|
| `POST` | `/organizations/{id}/invitations` | Invite team member by email | Yes |
| `GET` | `/organizations/{id}/invitations` | List pending invitations | Yes |
| `POST` | `/invitations/accept` | Accept invitation with token | Yes |
| `POST` | `/invitations/{id}/resend` | Resend invitation email | Yes |
| `DELETE` | `/invitations/{id}` | Revoke pending invitation | Yes |

## 5. Permission Endpoints
| Method | Path | Description | Auth Required |
|---|---|---|---|
| `GET` | `/permissions/me` | Get platform roles and permissions | Yes |
| `GET` | `/organizations/{id}/permissions/me` | Get organization-scoped permissions | Yes |

