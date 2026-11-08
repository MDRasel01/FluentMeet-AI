# Step 09 — Pronunciation Scoring Rubric & Gating

## 1. Deterministic Pronunciation Scoring Formula

The `PronunciationScorer` combines physical acoustic evidence into a calibrated 0–100 scale:

$$\text{Overall Pronunciation Score} = 0.40 \times W_{\text{acc}} + 0.25 \times P_{\text{fid}} + 0.15 \times S_{\text{stress}} + 0.10 \times I_{\text{intonation}} + 0.10 \times C_{\text{pace}}$$

Where:
- $W_{\text{acc}}$: Average word-level acoustic score.
- $P_{\text{fid}}$: Phoneme fidelity across consonants and vowels.
- $S_{\text{stress}}$: Word and sentence syllable stress prominence.
- $I_{\text{intonation}}$: Pitch contour modulation score.
- $C_{\text{pace}}$: Speaking pace tempo score.

---

## 2. Strict Evidence Gating (Zero-Fabrication Guarantee)

To prevent phantom score generation on silence, throat clearing, or single words:

| Gate Condition | Outcome | Stored Values |
| :--- | :--- | :--- |
| **Evaluated Words $< 5$** | Status $\rightarrow$ `insufficient_evidence` | `overall_pronunciation_score = None`<br>`evidence_confidence = 0.50`<br>`evidence_coverage = 0.0` |
| **Missing Physical Audio** | Status $\rightarrow$ `insufficient_evidence`<br>`audio_quality_status = "audio_missing"` | `overall_pronunciation_score = None`<br>`error_message_safe = "Acoustic audio evidence was missing"` |
| **Severe Clipping ($> 15\%$)** | Flagged as `low_quality` | Confidence penalized to $0.60$; explicit exclusion notes logged. |

---

## 3. Explicit Separation of Confidence & Coverage

- **Confidence ($[0.0, 1.0]$)**: Reflects mathematical and signal certainty of the measurement (SNR, ASR acoustic probability, and frame correlation).
- **Evidence Coverage ($[0.0, 1.0]$)**: The ratio of successfully evaluated words relative to total detected words:
  $$\text{Coverage} = \frac{\text{Evaluated Word Count}}{\text{Evaluated Word Count} + \text{Excluded Word Count}}$$
