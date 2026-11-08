# Step 08 — Vocabulary Intelligence Specification

## 1. Lexical Diversity Measurement (MATTR)
Standard Type-Token Ratio (TTR) is sensitive to total word length. To provide text-length independent lexical evaluation, FluentMeet AI computes **Moving-Average Type-Token Ratio (MATTR)**:
$$MATTR = \frac{1}{N - W + 1} \sum_{i=1}^{N - W + 1} \frac{\text{UniqueTokens}(w_i, \dots, w_{i+W-1})}{W}$$
where $W$ is the sliding window size (default $W=50$ words).
- **MATTR < 0.55**: Limited, highly repetitive vocabulary.
- **MATTR 0.55 - 0.70**: Healthy, diverse conversational English.
- **MATTR > 0.70**: Rich, versatile professional vocabulary.

## 2. Overused Phrase Detection & Executive Upgrades
Conversational crutch phrases are flagged and matched with elevated alternatives:
| Spoken Phrase | Upgraded Collocation | Register Focus |
|---|---|---|
| `good things` / `good stuff` | `favorable outcomes` / `valuable insights` | Executive Presence |
| `very big problem` | `significant obstacle` / `critical bottleneck` | Problem-Solving Precision |
| `make it better` | `optimize` / `streamline` / `enhance` | Strategic Action |
| `a lot of things` | `multiple initiatives` / `comprehensive items` | Clarity & Specificity |

## 3. Register-Calibrated Scoring
Vocabulary scoring is contextualized by the detected meeting register (`business`, `technical`, `interview`, `client_discussion`). Technical meetings encourage domain jargon (e.g., `latency`, `throughput`, `endpoints`), whereas executive business discussions emphasize strategic phrasing.

