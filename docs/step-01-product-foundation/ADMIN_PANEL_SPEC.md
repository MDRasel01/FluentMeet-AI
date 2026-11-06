# Admin Panel & Enterprise Operations Specification

**Product Name:** AI Meeting English Coach  
**Document ID:** SPEC-ADMIN-V1.0  
**Status:** Approved Operations Console Specification  
**Version:** 1.0.0  

---

## 1. Overview & Administration Scopes

The Admin Panel serves two distinct administrative levels:
1. **Super Admin Console (Internal / Platform Level):** Global visibility across all tenants, cloud infrastructure, AI model economics, and system health.
2. **Organization Admin Console (Customer / Tenant Level):** Customer-facing administrative interface for company-wide user provisioning, license seats, billing, and privacy policies.

---

## 2. Super Admin Console Specifications

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ Super Admin Top Bar: Env: Production │ Global Search │ System Health: Normal     │
├───────────────┬──────────────────────────────────────────────────────────────────┤
│ Navigation    │ KPI Metrics: Active Orgs (142) │ Processed Mins (84.2k) │ AI ($) │
│ • Dashboard   ├──────────────────────────────────────────────────────────────────┤
│ • Tenants     │ Live Infrastructure & AI Engine Health Monitor                   │
│ • Users       ├──────────────────────────────────────────────────────────────────┤
│ • AI Usage    │ Async Worker Queue Backlog & Failure Telemetry                   │
│ • Queues      ├──────────────────────────────────────────────────────────────────┤
│ • Audit Logs  │ Global Tenant & Organization Management Table                    │
└───────────────┴──────────────────────────────────────────────────────────────────┘
```

### 2.1 Section 01 — Executive KPI Dashboard
- **Total Registered Organizations:** Active, Trial, and Churned tenants.
- **Total Processed Audio Minutes:** Aggregated monthly volume of meeting audio.
- **Total AI Token Consumption:** Input and output tokens consumed across Google Gemini models.
- **Estimated Cloud Costs:** Real-time calculation of API spend (Gemini + ASR + Cloud Infrastructure) vs. ARR.
- **Queue Backlog & Processing Failure Rate:** Target < 0.5% failure rate.

### 2.2 Section 02 — Global User Management
- Search and filter across all platform users by email, tenant, role, and registration date.
- User detail drawer: Account status (`Active`, `Suspended`, `Pending Verification`), paired extensions, last login IP.
- Actions: Password reset dispatch, manual role override, tenant reassignment, and account suspension for abuse.

### 2.3 Section 03 — Multi-Tenant Organization Management
- Complete tenant list with provisioned seats, active subscriptions, and custom enterprise quotas.
- Manual tenant provisioning interface: Assign custom audio minute quotas, feature flags (e.g., enable experimental pronunciation engine), and enterprise SAML/SSO configs.

### 2.4 Section 04 — Subscription & Plan Management
- Manage SaaS tiers: Free Tier, Professional ($29/mo), Team ($19/seat/mo), Enterprise (Custom).
- Quota configuration: Monthly meeting minutes limit, maximum concurrent sessions, audio retention default days.

### 2.5 Section 05 — AI Usage & Cost Monitoring
- Real-time telemetry on Google Gemini API calls:
  - Average tokens per meeting minute.
  - Latency distribution (p50, p95, p99).
  - Pydantic schema validation failure rate.
  - Model distribution (e.g., Gemini 1.5 Flash vs. Pro).

### 2.6 Section 06 — System Health & Worker Queue Monitoring
- **FastAPI Core & WebSocket Gateways:** Active connections, throughput, CPU/Memory load.
- **Redis Streams & Celery Queue Backlog:** Number of pending audio processing tasks, active worker threads, and dead-letter queue count.
- **Real-time Error Log Stream:** Filterable stack traces and client-side extension error reports.

### 2.7 Section 07 — Audit Logs & Compliance Forensics
- Immutable log recording all administrative actions (role changes, quota modifications, tenant suspensions).
- Compliance audit trail: Logs of user consent assertion timestamps and automated data erasure executions (GDPR/CCPA verification).

---

## 3. Organization Admin Console (Customer-Facing)

Integrated into the main Web Dashboard under the **Organization** navigation group:

### 3.1 Member & Seat Management (`/settings/organization/members`)
- Seat utilization gauge: `18 of 25 Seats Used`.
- Member invitation modal: Batch invite colleagues via email and assign roles (`Team Member` or `Team Manager`).
- Team assignment dropdown: Allocate members to specific organizational departments.

### 3.2 Enterprise Privacy & Retention Policy (`/settings/organization/privacy`)
- Mandatory retention setting for all company employees:
  - Option A: Ephemeral (Audio discarded immediately after report generation).
  - Option B: 7-Day Compliance Window (Audio available for 7 days, then permanently erased).
  - Option C: 30-Day Window.
- Enforce mandatory recording consent prompt across all corporate extensions.

