# Step 11: 03 — Module Dependency & Package Isolation Report

**Module:** Dependency & Package Audit  
**Step:** 11 of 12  
**Target:** Python & Node.js Package Ecosystem  

---

## 1. Python Backend Dependencies (`services/api/pyproject.toml`)

| Dependency | Declared Version | Purpose | Security / License Status |
|---|---|---|---|
| `fastapi` | `^0.111.0` | High-performance asynchronous REST & WebSocket framework | Apache 2.0 (Permissive) |
| `uvicorn` | `^0.30.1` | ASGI server implementation | BSD-3-Clause (Permissive) |
| `sqlalchemy` | `^2.0.31` | Asynchronous ORM & query builder | MIT (Permissive) |
| `asyncpg` | `^0.29.0` | Asynchronous PostgreSQL driver | Apache 2.0 (Permissive) |
| `pydantic` | `^2.7.4` | Data validation & schema serialization | MIT (Permissive) |
| `pydantic-settings` | `^2.3.4` | Environment variable parsing | MIT (Permissive) |
| `redis` | `^5.0.7` | Asynchronous Redis client & stream consumer | MIT (Permissive) |
| `bcrypt` | `^4.1.3` | Cryptographic password hashing | Apache 2.0 (Permissive) |
| `pyjwt` | `^2.8.0` | JWT encoding & algorithm-allowlisted decoding | MIT (Permissive) |
| `google-genai` | `^0.1.1` | Google Gemini 2.5 Flash API SDK | Apache 2.0 (Permissive) |
| `numpy` | `^1.26.4` | Numerical signal processing & PCM byte slicing | BSD-3-Clause (Permissive) |
| `scipy` | `^1.13.1` | Acoustic feature analysis & F0 pitch extraction | BSD-3-Clause (Permissive) |

---

## 2. Node.js Frontend & Extension Dependencies

### Dashboard (`apps/dashboard/package.json`)
- `next`: `^14.2.35` — React Server Components & Static Site Generation
- `react`, `react-dom`: `^18.3.1`
- `lucide-react`: `^0.363.0` — Accessible SVG iconography
- `tailwind-merge`, `clsx`: Utility class merging

### Chrome Extension (`apps/extension/package.json`)
- `vite`: `^5.2.0` — Fast Manifest V3 bundle creation
- `vitest`: `^1.6.0` — Unit test execution in JSDOM environment
- `@fluentmeet/api-client`: Monorepo workspace package for API communication

---

## 3. Dependency Vulnerability Findings & Risk Mitigation

- **`pnpm audit` Finding**: Flags Next.js Windows dev advisory (GHSA-p293-qw3h-jr36).
  - *Risk Assessment*: In production environments, FluentMeet AI dashboard is deployed on Linux/containerized Alpine Docker images or static CDN edges, eliminating Windows-specific dev server exposure.
  - *Mitigation Plan*: Documented in Technical Debt Register (`DEBT-001`) with scheduled upgrade to Next.js 15.5+ for the next major release cycle.
