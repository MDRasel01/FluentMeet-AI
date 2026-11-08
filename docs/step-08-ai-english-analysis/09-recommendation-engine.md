# Step 08 — Recommendation Engine Specification

## 1. Principles of Actionable Feedback
Feedback is designed to be immediately actionable, positive, and grounded:
1. **Evidence-Anchored**: Every recommendation references an actual transcript quote or metric.
2. **Prioritized**: Ranked by impact (`high`, `medium`, `low`).
3. **Concrete Modeling**: Provides explicit `Before -> After` phrasing examples.
4. **Outcome-Oriented**: Defines the expected executive or communicative outcome.

## 2. Priority Hierarchy
- **High Priority**:
  - Recurring grammar errors (frequency >= 2 across session).
  - Excessive filler rate (> 6.0/min) requiring strategic pause practice.
  - Pervasive run-ons obscuring core arguments.
- **Medium Priority**:
  - Executive vocabulary upgrades (substituting basic conversational phrases).
  - Speech pacing adjustments (under 105 WPM or over 175 WPM).
  - Syntactic variety improvements.
- **Low Priority**:
  - Varying sentence opening transitions (`Basically` / `So yeah`).
  - Advanced stylistic and idiomatic polish.

## 3. Deduplication & Capping
The recommendation engine caps output to the top **5–7 highest-impact recommendations** per meeting to prevent cognitive overload.

