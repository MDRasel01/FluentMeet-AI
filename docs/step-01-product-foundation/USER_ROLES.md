# User Roles, Permissions & Tenant Isolation

**Product Name:** AI Meeting English Coach  
**Document ID:** SPEC-ROLES-V1.0  
**Status:** Approved Access Control Specification  
**Version:** 1.0.0  

---

## 1. User Hierarchy & Role Definitions

The platform implements a multi-tenant Role-Based Access Control (RBAC) model supporting both standalone individuals (B2C) and structured enterprise organizations (B2B).

```
                      ┌─────────────────────────┐
                      │       Super Admin       │ (Platform Operator)
                      └────────────┬────────────┘
                                   │ Manages all tenants
                                   ▼
                      ┌─────────────────────────┐
                      │   Organization Admin    │ (Enterprise Customer)
                      └────────────┬────────────┘
                                   │ Manages Org & Billing
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
        ┌─────────────────────────┐ ┌─────────────────────────┐
        │      Team Manager       │ │       Team Member       │
        │  (Scoped Team Insights) │ │  (Private Self-Reports) │
        └─────────────────────────┘ └─────────────────────────┘

[ Separate B2C Tier ] ──► ┌─────────────────────────┐
                           │     Individual User     │ (Personal Subscription)
                           └─────────────────────────┘
```

---

### 1.1 Individual User (B2C / Standalone)
- **Description:** A private professional using their personal subscription to analyze meetings and improve their spoken English.
- **Scope of Data:** Access is strictly confined to their own personal account. They cannot belong to an enterprise organization workspace or invite teammates.
- **Primary Capabilities:**
  - Authenticate Chrome Extension on personal Google/Zoom/Teams accounts.
  - Record personal meeting sessions and access full audio, transcripts, and reports.
  - Review personal English Scores (Grammar, Vocabulary, Fluency, Pronunciation, IELTS).
  - Practice personalized AI micro-lessons in the Learning Center.
  - Manage personal billing, upgrade plans, and export/delete personal data.

---

### 1.2 Team Member (B2B Organization Seat)
- **Description:** An employee of a company holding an active seat in an enterprise workspace.
- **Scope of Data:** Can only access their own meeting recordings, private transcripts, and personal evaluation reports.
- **Primary Capabilities:**
  - Connect enterprise SSO / Google Workspace account.
  - Record enterprise meetings via the Chrome Extension.
  - Review personal reports, mistake history, and practice recommendations.
  - Opt into or out of team-shared meeting transcripts based on company policy.
- **Privacy Boundary:** A Team Member's raw speaking mistakes and individual pronunciation scores are **private by default**. Team Managers only view aggregated statistical trends unless explicit collaborative coaching mode is enabled.

---

### 1.3 Team Manager (B2B Team Lead)
- **Description:** A leader supervising one or more functional teams (e.g., Engineering Team Lead, Customer Support Manager).
- **Scope of Data:** Scoped exclusively to assigned teams within their organization. Cannot view other departments or global billing details.
- **Primary Capabilities:**
  - View aggregate **Team Analytics** (average team speaking pace, most frequent grammar mistake categories, vocabulary growth index).
  - View authorized team meeting summaries and aggregate participant participation percentages.
  - Assign organizational learning objectives or recommended practice topics.
- **Explicit Limitations & Privacy Rules:**
  - **No Unconsented Spying:** Cannot inspect a team member's personal practice results or detailed mistake log from 1-on-1 private meetings without explicit consent.
  - **Aggregated View:** Member comparison reports show cohort distributions and high-level proficiency tiers rather than embarrassing verbatim mistake transcripts.

---

### 1.4 Organization Admin (B2B Enterprise Admin / HR Lead)
- **Description:** The organizational authority managing the SaaS contract, member provisioning, and enterprise compliance.
- **Scope of Data:** Entire organization workspace (all teams, members, seats, and billing). Cannot access platform-wide Super Admin tools.
- **Primary Capabilities:**
  - Invite, suspend, and remove team members; assign manager roles.
  - Create and restructure organizational teams and departments.
  - Manage enterprise subscription tiers, seat expansion, payment methods, and invoices.
  - Define data retention policies (e.g., auto-purge meeting audio after 7 days for enterprise compliance).
  - Monitor aggregated organization usage (total meeting minutes, audio processing hours).

---

### 1.5 Super Admin (Platform Operator / Antigravity Staff)
- **Description:** Internal system administrator responsible for the stability, economics, and integrity of the SaaS ecosystem.
- **Scope of Data:** Global access across all tenants, users, worker queues, and infrastructure.
- **Primary Capabilities:**
  - Global User & Tenant Management (suspend malicious accounts, adjust plan quotas).
  - AI Usage & Cost Auditing (Gemini token consumption, cost per meeting minute, API latency).
  - Infrastructure Health Oversight (Redis queue backlog, worker pool saturation, ASR failure telemetry).
  - Feature Flag Management (enable experimental pronunciation models or new platform adapters).

---

## 2. Granular Role-Permission Matrix

| Resource / Action | Individual User | Team Member | Team Manager | Org Admin | Super Admin |
|---|:---:|:---:|:---:|:---:|:---:|
| **Record Meeting via Extension** | Own | Own | Own | Own | Any (Demo) |
| **View Own Transcripts & Audio** | Yes | Yes | Yes | Yes | Audit only |
| **View Teammate Transcripts** | N/A | No | Policy-Gated | Policy-Gated | Audit only |
| **View Own English Report** | Yes | Yes | Yes | Yes | Yes |
| **View Teammate Detail Mistakes** | N/A | No | No (Aggregated Only) | No | Audit only |
| **Access Team Analytics Dashboard** | No | No | Assigned Teams | All Org Teams | Global |
| **Access Learning Center Drills** | Yes | Yes | Yes | Yes | Yes |
| **Assign Team Practice Modules** | No | No | Yes | Yes | Yes |
| **Manage Org Members & Roles** | No | No | Team Assign Only | Full Org | Global |
| **Configure Audio Retention Policy** | Personal | No | No | Full Org | Global |
| **Manage Billing & Payment** | Personal | No | No | Full Org | Global |
| **View AI Token & Cloud Costs** | No | No | No | Org Quotas | Global System |
| **Inspect Worker Queues & Errors** | No | No | No | No | Yes |
| **Hard Delete Meeting & Audio Data** | Own | Own | No | Org-Wide | Global System |

---

## 3. Organization Hierarchy & Tenant Scoping Rules

```
Organization (tenant_id: UUID)
├── Subscription Plan (Tier: Pro/Team/Enterprise, Quota: Minutes/Mo)
├── Retention Policy (Audio TTL: 7/30/90 Days)
├── Teams (team_id: UUID)
│   ├── Team Manager (user_id: UUID, role: manager)
│   └── Team Members (user_id: UUID, role: member)
└── Organization Admins (user_id: UUID, role: org_admin)
```

1. **Strict SQL Scoping:** Every relational query on meetings, transcripts, and analysis must include `WHERE tenant_id = :auth_tenant_id`.
2. **Manager Scoping:** Queries by Team Managers on team aggregates must join on the `team_members` junction table to prevent horizontal escalation into unrelated company departments.
3. **Data Erasure Compliance:** When an Organization Admin or Individual invokes `FR-028 (Data Deletion)`, all associated records in Postgres, chunks in S3, and cached items in Redis must be cryptographically deleted within 72 hours.

