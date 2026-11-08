# Step 08 — Fluency Analytics Specification

## 1. Timing-Based Telemetry
Using millisecond boundaries from Step 07 speech-to-text segments, the engine extracts four objective fluency metrics:

### 1.1 Speech Rate (Words Per Minute — WPM)
$$WPM = \frac{\text{Total Spoken Words}}{\text{Total Active Speaking Duration (Minutes)}}$$
- **Optimal Professional Range**: 125 – 165 WPM.
- **Under 100 WPM**: Hesitant, slow delivery; penalizes speaking momentum.
- **Over 175 WPM**: Rushed delivery; risks comprehension failure in multi-national meetings.

### 1.2 Filler Word Rate
Detects conversational hesitation fillers: `um`, `uh`, `er`, `like`, `you know`, `actually`, `basically`, `so yeah`, `i mean`, `sort of`, `kind of`.
$$\text{Filler Rate} = \frac{\text{Count of Filler Words}}{\text{Total Active Speaking Duration (Minutes)}}$$
- **<= 2.0 / min**: Excellent, clean delivery (Score: 100).
- **2.0 - 5.0 / min**: Moderate conversational filler usage.
- **> 6.0 / min**: High frequency; triggers dedicated coaching recommendations for silent pauses.

### 1.3 Hesitation Repetition Rate
Measures immediate syllable or word repetitions (`we we`, `the the`, `I I`) per 100 words:
$$\text{Repetition Rate} = \left(\frac{\text{Repeated Token Pairs}}{\text{Total Words}}\right) \times 100$$

### 1.4 Turn Pausing & Utterance Length
- Computes pause gaps between speaker turns (> 1200ms).
- Measures average utterance length (words per turn) to evaluate conversational cadence.

