# Step 11: 09 — Technical Debt Register & Maintenance Backlog

**Module:** Technical Debt Register  
**Step:** 11 of 12  

---

## 1. Technical Debt Inventory

| Debt ID | Module | Description | Impact | Priority | Recommended Action | Target Phase |
|---|---|---|---|---|---|---|
| **DEBT-001** | `apps/dashboard` | Next.js `14.2.35` upgrade to Next.js `15.5+` | Security advisories on Windows dev server | Medium | Upgrade Next.js & React 19 in major version bump | Step 12 Post-Launch |
| **DEBT-002** | `services/api` | Starlette `python-multipart` deprecation notice | Starlette deprecates `multipart` import | Low | Transition import to `python_multipart` | Routine Maintenance |
| **DEBT-003** | `services/api` | Python 3.16 asyncio `inspect.iscoroutinefunction` notice | Future deprecation in Python 3.16 | Low | Fastapi/Starlette upstream update will resolve | Python 3.16 Migration |
| **DEBT-004** | `apps/extension` | AudioWorklet fallback for older Chromium $< 109$ | Incompatible with legacy Chrome versions | Low | Document Chrome $\ge 116$ minimum requirement | Production Docs |

---

## 2. Debt Management Strategy

None of the registered technical debt items block production release. Items with security implications (`DEBT-001`) are mitigated by containerized Linux production deployment.

