# Audio Temporal Synchronization & Clock Integrity
## Specification: Step 05 — Section 10

---

## 1. Synchronization Challenge

Because tab audio and microphone audio are captured through separate hardware and clock domains, standard system clock (`Date.now()`) will exhibit clock drift, NTP adjustments, or time-zone step changes during long meetings.

To ensure sample-accurate alignment on the backend:
1. **Monotonic Session Reference:** All chunk timestamps are calculated using `performance.now() - sessionStartMonoTime` (`monotonic-clock.ts`).
2. **Independent Monotonic Sequence Numbers:** Tab audio chunks increment `tabSequenceNumber` from $0, 1, 2, \dots$; microphone audio chunks increment `micSequenceNumber` from $0, 1, 2, \dots$.
3. **Session Start Anchor:** An absolute UTC wall-clock timestamp is recorded at session start and transmitted in `session_init`, providing an immutable anchor point for server-side mapping.

---

## 2. Temporal Alignment Equation

For any audio chunk with sequence number $S$ and session relative timestamp $T_{\text{mono}}$:

$$ T_{\text{server}} = T_{\text{session\_anchor}} + T_{\text{mono}} $$

$$ \text{Expected Sample Offset} = S \times N_{\text{chunk\_samples}} $$

$$ \text{Clock Drift Metric} = \left| T_{\text{mono}} - \frac{S \times N_{\text{chunk\_samples}}}{f_{\text{sample}}} \times 1000 \right| $$

If the backend observes a discrepancy between $T_{\text{mono}}$ and the sample count exceeding 50 ms, an acoustic drift compensation filter or padding frame is inserted rather than corrupting audio pitch.

