# Step 10 — Individual Participant Detailed Report Specification

**Module:** Participant Performance Reports  
**Component:** `app.reports.builder.ParticipantReportBuilder`  

---

## 1. Overview

Each participant who contributed spoken audio during a meeting receives an independent, private assessment report.

## 2. Key Report Dimensions

1. **Overall English Score:** Calibrated index out of 100 with confidence metric.
2. **Speaking Metrics:** Total word count, elapsed speaking duration, and speaking pace in words per minute (WPM).
3. **Grammar Accuracy Analysis:**
   - Detailed corrections list:
     - `rule_type`: Syntactic category (e.g. `subject_verb_agreement`, `prepositions`).
     - `offending_text`: The exact phrase spoken.
     - `corrected_text`: Recommended grammatical replacement.
     - `explanation`: Pedagogical rationale.
     - `severity`: Impact level (`minor`, `moderate`, `major`).
4. **Vocabulary Precision & Lexical Diversity:**
   - High-impact professional expressions used.
   - Overused or repetitive words flagged for variety.
5. **Fluency & Temporal Metrics:**
   - Words per minute (WPM).
   - Filler word frequency and pause distributions.
   - Speech rate classification (`moderate`, `brisk`, `deliberate`).
6. **Pronunciation & Acoustic Observations:**
   - Word-level phonetic accuracy percentages.
   - Expected ARPAbet/IPA phonemes vs. observed acoustic productions.
   - Prosodic pitch variation and sentence stress.
7. **IELTS Practice Estimate:**
   - Overall band estimate and 4 sub-bands (Fluency, Lexical, Grammar, Pronunciation).
   - Approximate CEFR level (`B2`, `C1`).
   - Qualitative band descriptor summary.
   - **Mandatory Educational Disclaimer.**
8. **Personalized Drills:** Actionable speaking drills with customized practice sentences.

