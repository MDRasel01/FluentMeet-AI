# Step 08 — Scoring Rubric & Dynamic Normalization Specification

## 1. Weighted Composite Formula
FluentMeet AI computes an overall communicative competency score on a 0–100 scale:

| Category | Weight | Description |
|---|---|---|
| **Grammar** | 25% (0.25) | Structural correctness, tenses, subject-verb agreement |
| **Vocabulary** | 20% (0.20) | Lexical diversity (MATTR), precision, collocations |
| **Fluency** | 20% (0.20) | Speech pace (WPM), filler frequency, rhythm |
| **Sentence Structure** | 10% (0.10) | Clause complexity, variety, run-on elimination |
| **Communication** | 15% (0.15) | Active listening, diplomatic framing, relevance |
| **Contextual Language** | 10% (0.10) | Alignment with domain and formality expectations |
| **Total** | **100% (1.00)** | Balanced composite |

## 2. Dynamic Denominator Normalization
If a category cannot be evaluated or contains insufficient data, its weight is **not substituted with 0.0**. Doing so would artificially depress the participant's score.
Instead, the denominator dynamically re-normalizes over the available category subset:
$$Score_{overall} = \frac{\sum_{c \in Available} w_c \times S_c}{\sum_{c \in Available} w_c}$$

## 3. Minimum Speech Data Gate
If a participant speaks:
- Fewer than **50 words**, OR
- Less than **15.0 seconds** of active speaking time,

The engine flags the participant as `status = "insufficient_data"`, sets `overall_score = NULL`, and outputs individual category scores as `insufficient_data`. This guarantees fair assessments and eliminates false negative ratings.
