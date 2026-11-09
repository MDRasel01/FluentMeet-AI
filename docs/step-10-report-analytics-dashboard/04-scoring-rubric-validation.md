# Step 10 — Scoring Rubric & Validation Engine Specification

**Module:** Quality Assurance & Score Calibration  
**Component:** `app.reports.validator.ReportValidationEngine`  

---

## 1. Principles of Deterministic Calibration

The Report Engine strictly formats and calibrates upstream evidence from Steps 08 and 09. Under no circumstances does the engine fabricate scores or fill in missing categories with arbitrary default values.

## 2. Core Validation Rules

### 2.1 Evidence Threshold Gate
- **Minimum Word Threshold:** `MIN_EVALUATED_WORDS = 5`
- If evaluated words < 5:
  - `report_status = "insufficient_evidence"`
  - `overall_score = None`
  - `status_label = "Insufficient speech evidence for calibrated score"`
  - `missing_components = ["insufficient_speech"]`

### 2.2 Missing Component Handling (Zero-Fabrication Guarantee)
- The 4 core pillars required for complete score calibration are:
  1. `Grammar Accuracy` (Step 08)
  2. `Vocabulary Range` (Step 08)
  3. `Fluency & Pace` (Step 08)
  4. `Acoustic Pronunciation` (Step 09)
- If any of these four pillars is missing:
  - The engine **NEVER** substitutes 0.
  - The engine **NEVER** estimates without evidence.
  - `overall_score = None`
  - `report_status = "partial"`
  - `status_label = "Overall score unavailable"`
  - `missing_components` explicitly lists the missing dimensions (e.g. `["pronunciation"]`).

### 2.3 Calibrated Score Calculation
- When all 4 core pillars are validated and present:
  $$\text{Overall Score} = \text{round}\Big(0.25 \times G + 0.25 \times V + 0.25 \times F + 0.25 \times P, 1\Big)$$
- `report_status = "completed"`
- `status_label = "Calibrated"`
- Confidence is calculated as the blended mean of Step 08 and Step 09 evidence confidences.

