# Super Admin Panel High-Fidelity UI Specification

**Product Name:** AI Meeting English Coach  
**Document ID:** ADMIN-DESIGN-V1.0  
**Phase:** Step 02  
**Implemented Screens:** 13 / 13 Screens (100%)  
**Status:** Approved Admin Operations Baseline  

---

## 1. Overview & Operational Shell

The Super Admin Console provides platform-wide observability, infrastructure governance, multi-tenant subscription management, and AI model economics. Designed with a high-contrast dark aesthetic (`bg-slate-900` / `bg-slate-950`), it ensures immediate visibility into critical telemetry and operational bottlenecks.

---

## 2. Comprehensive 13-Screen Specifications

### Screen 01 — Admin Overview
- **Purpose:** Executive dashboard monitoring cross-tenant growth, audio volume, and infrastructure stability.
- **UI Sections:**
  - 4 Key Operational Metrics: Total Registered Tenants (84), Processed Audio Minutes (148,520), Gemini Token Spend (124.6M tokens / $642.80 cost), and Processing Backlog (3 tasks).
  - Infrastructure Status Panel: Real-time health gauges for FastAPI Gateway, WebSocket Streamers, and Redis clusters.

### Screen 02 — User Management Directory
- **Purpose:** Centralized directory of all 1,420 registered users across all enterprise tenants.
- **UI Sections:**
  - Searchable user table displaying full name, email, tenant organization, role, meeting count, account status (`Active`, `Suspended`), and "Inspect" triggers.

### Screen 03 — User Details & Forensics
- **Purpose:** Deep inspection drawer for a selected user account.
- **UI Sections:**
  - Email verification state, assigned tenant ID, Chrome Extension pairing token ID, and admin action buttons ("Impersonate Session", "Suspend User").

### Screen 04 — Organization & Tenant Management
- **Purpose:** Multi-tenant account registry and seat provisioning.
- **UI Sections:**
  - Organization table displaying tenant name (e.g., Acme Corp, TechFlow Global), active plan tier, seat capacity utilization (e.g., `25 / 40 seats`), and retention window.

### Screen 05 — Organization Details
- **Purpose:** Granular tenant configuration.
- **UI Sections:**
  - Subscription breakdown, allocated monthly meeting minute quotas, and custom retention policy overrides.

### Screen 06 — Subscription Management
- **Purpose:** Customer billing health and revenue metrics.
- **UI Sections:**
  - Overview of 78 active paid subscriptions, Monthly Recurring Revenue (MRR: $18,420), and churn risk indicators.

### Screen 07 — Plan Tier Configuration
- **Purpose:** Defining SaaS pricing plans, seat costs, and feature gates.
- **UI Sections:**
  - Configuration cards for Individual Pro ($29/mo), Team Tier ($19/seat/mo), and Enterprise Custom.

### Screen 08 — AI Usage & Model Economics
- **Purpose:** Detailed telemetry on Google Gemini API token usage and cost forecasting.
- **UI Sections:**
  - Total tokens consumed, average tokens per meeting minute (840 tokens/min), and Pydantic schema validation success rates (99.98%).

### Screen 09 — Processing Queue Management
- **Purpose:** Real-time visibility into the asynchronous Celery / Redis task queue.
- **UI Sections:**
  - Active worker node count (12/16 active), queue latency distribution (420ms p95), and dead-letter queue count (0).

### Screen 10 — System Monitoring & Infrastructure
- **Purpose:** Hardware and service connectivity telemetry.
- **UI Sections:**
  - Live status feeds for database connection pool utilization (18%), WebSocket concurrency (1,240 active connections), and CPU/RAM saturation.

### Screen 11 — Error Telemetry & Logs
- **Purpose:** Real-time filterable log stream for platform debugging.
- **UI Sections:**
  - Monospace log feed with timestamped log levels (`[INFO]`, `[WARN]`, `[ERROR]`), capturing server exceptions and client-side extension recovery events.

### Screen 12 — Compliance & Governance Audit Trail
- **Purpose:** Immutable audit log satisfying enterprise compliance (SOC2 Type II / GDPR).
- **UI Sections:**
  - Filterable audit table recording administrative actions: user consent assertion events, tenant seat expansions, role changes, and automated audio file purges.

### Screen 13 — Admin Platform Settings
- **Purpose:** Global emergency controls and configuration.
- **UI Sections:**
  - Maintenance Mode toggle (temporarily queueing or rejecting new recording sessions), global rate limit adjustments, and API credential rotation.

