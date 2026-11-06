# Organization & Team Management

## 1. Multi-Tenant Organization Lifecycle
- **Creation (`POST /api/v1/organizations`):**
  - Name, custom slug (or auto-generated slug), organization type, timezone, default language.
  - Creator is automatically assigned the **Owner** role in `organization_members`.
  - Default `organization_settings` are provisioned atomically.
- **Listing (`GET /api/v1/organizations`):**
  - Returns organizations the user belongs to along with their specific role.
- **Details (`GET /api/v1/organizations/{id}`):**
  - Tenant-scoped: verified against caller's active membership.

## 2. Team Invitation Workflow
1. Owner / Admin / authorized Manager sends an invitation:
   - `POST /api/v1/organizations/{id}/invitations`
   - Validates that target role does not exceed caller's role (escalation prevention).
   - Generates a 7-day single-use invitation token.
2. Recipient accepts:
   - `POST /api/v1/invitations/accept`
   - Strictly enforces that the caller's email matches the invitation target email.
   - Creates or activates membership with the assigned role.

## 3. Ownership Transfer
- **Endpoint:** `POST /api/v1/organizations/{id}/transfer-ownership`
- **Rules:**
  - Caller must be the current Owner.
  - Password re-authentication is mandatory.
  - New owner must be an active member of the organization.
  - Old owner is transitioned to Admin.
  - Audit event is logged with actor and new owner IDs.

