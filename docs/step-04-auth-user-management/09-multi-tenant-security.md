# Multi-Tenant Security & Isolation Strategy

## 1. Tenant Isolation Principles
In FluentMeet AI, multiple enterprise organizations co-exist within the same shared database schema. Tenant boundaries must be impenetrable:
1. **Never Trust Client-Supplied Organization IDs:** The incoming `organization_id` in URL parameters or headers is strictly verified against the database to confirm the authenticated user has an active membership record in that organization.
2. **Repository Layer Scoping:** All database queries for organization data (members, settings, invitations, meetings, analytics) must enforce an explicit filter on `organization_id`.
3. **No IDOR / BOLA Vulnerabilities:** Attempting to query another tenant's resource ID results in an immediate `403 Forbidden` or `404 Not Found` response.

## 2. Automated Isolation Verification
Our automated test suite (`tests/test_multi_tenancy.py`) verifies:
- Member of Org A requesting Org B details -> `403 Forbidden`.
- Member of Org A listing Org B members -> `403 Forbidden`.
- Member of Org A inviting an email to Org B -> `403 Forbidden`.
- Member of Org A attempting to delete Org B -> `403 Forbidden`.

