# Step 09 — Prosody, Pitch & Stress Analysis

## 1. Overview & Mechanics

Prosody represents the melodic and rhythmic structure of speech. In professional international communication, appropriate pitch modulation and stress placement convey certainty, questioning, enthusiasm, and phrase boundaries.

The `ProsodyAnalysisEngine` extracts fundamental frequency ($F_0$) contours, classifies intonation patterns, and measures syllable prominence.

---

## 2. Fundamental Frequency ($F_0$) Extraction

Pitch is extracted from 30ms Hamming-windowed acoustic frames with a 15ms hop interval using normalized autocorrelation:

$$r_x(\tau) = \frac{\sum_{n=0}^{N-1-\tau} x[n] x[n+\tau]}{\sqrt{\sum_{n=0}^{N-1-\tau} x^2[n] \sum_{n=0}^{N-1-\tau} x^2[n+\tau]}}$$

Lag intervals are constrained to human vocal speech ranges ($[75.0\text{ Hz}, 400.0\text{ Hz}]$). Peaks with correlation coefficients $r_x(\tau) \ge 0.40$ are identified as voiced pitches ($F_0 = f_s / \tau$).

---

## 3. Dynamic Intonation Classification

The pitch series across utterances is classified into distinct conversational contours:
- **Rising (`rising`)**: Second half mean pitch exceeds first half by $> 15\text{ Hz}$ (typical for inquiry, open questions, or engaged checking).
- **Falling (`falling`)**: Second half drops by $> 15\text{ Hz}$ below first half (signals declarative closure and assertive conclusions).
- **Complex (`complex`)**: Pitch range exceeds $45\text{ Hz}$ with multiple inflection points (indicative of dynamic, expressive executive communication).
- **Monotone / Level (`level`)**: Pitch range remains narrow ($\le 25\text{ Hz}$), indicating flat delivery.

---

## 4. Syllable & Word Stress Prominence

Word stress accuracy is evaluated by calculating root-mean-square energy contrast between primary stressed syllables and unstressed vowel nuclei. Stressed syllables must exhibit:
1. Higher acoustic amplitude ($\Delta \text{RMS} \ge 2.5\text{ dB}$).
2. Extended vowel duration ($\Delta T \ge 35\%$).
3. Elevated local fundamental frequency ($\Delta F_0 \ge 12\text{ Hz}$).

Monotone delivery without syllable prominence is identified, triggering stress modulation exercises.

