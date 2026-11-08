# Step 09 — Speaking Pace & Speech Intelligibility

## 1. Speaking Pace & Pause Taxonomy

The `SpeakingPaceAnalyzer` tracks conversational tempo, rhythm stability, and pause distribution.

### 1.1 Temporal Tempo Calculation
Speaking rate is computed across conversational intervals:
$$\text{WPM} = \frac{\text{Total Words Evaluated}}{(\text{Elapsed Speech Duration in ms}) / 60000.0}$$
$$\text{SPM (Syllables/Min)} = \text{WPM} \times 1.45$$

Optimal business conversational English operates within **130 – 165 WPM**. Rates exceeding $180\text{ WPM}$ lead to consonant cluster compression (`rushed`), while rates below $100\text{ WPM}$ signal hesitation or vocabulary retrieval bottlenecks (`hesitant`).

### 1.2 Pause Classification Matrix

| Gap Duration | Classification | Interpretation |
| :--- | :--- | :--- |
| **$< 150\text{ ms}$** | Coarticulation Transition | Sub-perceptual inter-word acoustic transition. |
| **$150\text{ ms} - 600\text{ ms}$** | `normal_pause` | Natural breathing and grammatical clause boundary. |
| **$600\text{ ms} - 1200\text{ ms}$** | `short_hesitation` | Mild hesitation or lexical choice formulation. |
| **$> 1200\text{ ms}$** | `long_hesitation` | Significant pause; monitored for fluency impact. |

---

## 2. Speech Clarity & Intelligibility (Accent-Neutral)

### 2.1 Core Principle: Intelligibility Over Native Conformity
FluentMeet AI assesses spoken English across distributed global teams. Speakers with European, Asian, Latin American, or African accents frequently communicate with pristine clarity and effectiveness. **Accents are never penalized.**

### 2.2 Composite Intelligibility Formula
Intelligibility is synthesized from two objective acoustic dimensions:

$$\text{Intelligibility} = 0.60 \times \text{Phonemic Clarity} + 0.40 \times \text{Acoustic Clarity}$$

Where:
- **Acoustic Clarity**: Reflects acoustic signal integrity, SNR projection, and absence of clipping distortion:
  $$\text{Acoustic Clarity} = \min(100.0, \max(50.0, 70.0 + 0.8 \times \text{SNR} - 100.0 \times \text{Clipping}))$$
- **Phonemic Clarity**: Reflects distinctness of consonant and vowel contrasts:
  $$\text{Phonemic Clarity} = \min(100.0, \max(50.0, 0.90 \times \text{Avg Phoneme Score} + 15.0 \times \text{Avg ASR Confidence}))$$

### 2.3 Qualitative Intelligibility Tiers
- **$\ge 85.0$**: `High intelligibility` — Speech is effortless to understand across international audiences.
- **$70.0 - 84.9$**: `Generally intelligible` — Speech is clear with occasional minor phonetic blur.
- **$< 70.0$**: `Partially difficult to understand` — Frequent acoustic masking or consonant reductions.
