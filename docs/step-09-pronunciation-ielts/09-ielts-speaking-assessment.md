# Step 09 — IELTS-Style Speaking Practice Assessment

## 1. Purpose & Core Philosophy

The `IELTSAssessmentEngine` provides learners with an educational, indicative practice band score modeled on international CEFR/IELTS four-dimension assessment rubrics.

> [!IMPORTANT]
> **Educational Practice Disclaimer**:
> "Educational practice estimate only. This is not an official IELTS score, certified assessment, or substitute for an IELTS examiner."
> This disclaimer is stored in the database (`disclaimer_text`) and delivered with every API response.

---

## 2. Four Assessment Dimensions

The engine synthesizes evidence from Step 08 and Step 09:

1. **Fluency & Coherence ($FC$)**: Derived from Step 08 fluency metrics and Step 09 pause/WPM analysis.
2. **Lexical Resource ($LR$)**: Derived from Step 08 vocabulary range and sophistication insights.
3. **Grammatical Range & Accuracy ($GRA$)**: Derived from Step 08 syntactic structures and grammar correctness.
4. **Pronunciation ($P$)**: Derived strictly from Step 09 acoustic evidence (phoneme fidelity, stress, intonation, intelligibility).

---

## 3. Score-to-Band Mapping & Rounding

Individual 0–100 category scores map to 0.5 IELTS band increments:

| 0–100 Score Range | Indicative Band | Qualitative Level |
| :---: | :---: | :--- |
| $\ge 94.0$ | **9.0** | Expert Speaker |
| $89.0 - 93.9$ | **8.5** | Very Good Speaker |
| $84.0 - 88.9$ | **8.0** | Very Good Communicator |
| $79.0 - 83.9$ | **7.5** | Good Professional Communicator |
| $74.0 - 78.9$ | **7.0** | Good User |
| $68.0 - 73.9$ | **6.5** | Competent User |
| $60.0 - 67.9$ | **6.0** | Competent Speaker |
| $54.0 - 59.9$ | **5.5** | Modest Communicator |
| $48.0 - 53.9$ | **5.0** | Modest User |
| $< 48.0$ | **4.0 – 4.5** | Developing Speaker |

### IELTS Rounding Rule
The arithmetic mean of the four dimensions is rounded to the nearest half-band:
$$\text{Raw Average} = \frac{FC + LR + GRA + P}{4}$$
$$\text{Overall Band} = \frac{\text{round}(\text{Raw Average} \times 2.0)}{2.0}$$
*Examples:*
- $6.25 \rightarrow \mathbf{6.5}$
- $6.75 \rightarrow \mathbf{7.0}$
- $6.125 \rightarrow \mathbf{6.0}$

