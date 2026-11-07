# Testing & Quality Assurance Strategy
## Specification: Step 05 — Section 20 & Section 21

---

## 1. Testing Pyramid

Testing for Step 05 spans four automated and semi-automated layers:

1. **Static Analysis & Type Checking:**
   - TypeScript 5.4+ under `strict: true` across `apps/extension`.
   - Zod runtime schema validation for cross-context runtime messages.
2. **Unit & Mathematical Signal Tests (Vitest):**
   - Precise validation of linear interpolation downsampling algorithms.
   - Bit-level verification of binary frame serialization and deserialization.
   - Finite State Machine transition coverage (valid vs. disallowed transitions).
3. **Component & User Interaction Tests (React Testing Library + JSDOM):**
   - Verification of all 15 React screens.
   - Mandatory consent checkbox gate before capture arming.
   - Dual VU meter rendering and active session timer updates.
4. **Backend Integration & Ingestion Tests (FastAPI + Starlette TestClient + Pytest):**
   - Verification of meeting session lifecycle routes (`/start`, `/pause`, `/resume`, `/stop`, `/complete`).
   - Binary WebSocket frame consumption and structured `audio_ack` responses.

