# Role-Based Access Control (RBAC) & Permission Matrix

## 1. Role Architecture
FluentMeet AI maintains strict separation between **Platform Roles** and **Organization Roles**:

### Platform Roles
- `super_admin`: Full system oversight, tenant administration, global configurations.
- `support_admin`: Customer support, diagnostics, assisted account recovery.
- `platform_analyst`: Read-only aggregated platform metrics and anonymized telemetry.
- `individual`: Standard end-user account.

### Organization Roles
- `owner`: Full control over the organization, ownership transfer, organization deletion.
- `admin`: Member management, settings, billing, team analytics.
- `manager`: Team member invitations (if allowed by settings), analytics viewing.
- `member`: Personal meeting participation and private coaching reports.

## 2. Organization Permission Matrix
| Permission | Owner | Admin | Manager | Member |
|---|---|---|---|---|
| `org:view` | ✓ | ✓ | ✓ | ✓ |
| `org:edit_settings` | ✓ | ✓ | — | — |
| `org:invite_members` | ✓ | ✓ | ✓* | — |
| `org:remove_members` | ✓ | ✓ | — | — |
| `org:change_roles` | ✓ | ✓* | — | — |
| `org:view_analytics` | ✓ | ✓ | ✓ | — |
| `org:view_reports` | ✓ | ✓ | ✓ | ✓ (Own) |
| `org:manage_subscription` | ✓ | ✓ | — | — |
| `org:transfer_ownership` | ✓ | — | — | — |
| `org:delete` | ✓ | — | — | — |

*\* Note: Manager invite permissions can be toggled via `allow_manager_invites` organization setting. Admins cannot promote anyone to Owner or alter Owner roles.*

## 3. Privilege Escalation Prevention
- Every role assignment is validated against `ROLE_HIERARCHY`:
  - `owner` (40) > `admin` (30) > `manager` (20) > `member` (10).
- An actor can only assign or manage roles with a strictly lower hierarchy value than their own.

