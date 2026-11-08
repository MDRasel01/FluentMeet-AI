# Step 08 — Speech Analysis Pipeline Specification

## 1. Overview & Data Flow
The Step 08 Speech Analysis Pipeline consumes finalized multi-speaker transcripts from Step 07 and transforms them into participant-specific linguistic telemetry and personalized coaching plans.

```
+-------------------------------------------------------------+
| Step 07: Verified Transcripts (PostgreSQL / Redis Streams)  |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Preprocessing Engine                                         |
| - Text normalization (Unicode quotes, control char strip)   |
| - Sliding context window builder with token budgeting        |
| - Low-confidence segment tagging (confidence < 0.65)         |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Context & Register Detection                                |
| - Lexical domain detection: Business, Technical, Interview,  |
|   Client Discussion, Casual                                  |
| - Formality calibration                                     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Parallel Linguistic Intelligence Execution                  |
| - Grammar Analyzer (ESL rules + Gemini structured JSON)     |
| - Vocabulary Analyzer (MATTR, overused phrases, collocations)|
| - Fluency Analyzer (WPM, filler rate, stutter repetitions)  |
| - Sentence Structure (Clause coordination, run-on detection)|
| - Communication Analyzer (Active listening, diplomacy)       |
| - Speaking Pattern Discovery (Multi-turn recurring habits)   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Evidence Verification Gate (Zero-Hallucination Guard)       |
| - Verifies segment_id against meeting speaker database      |
| - Verifies quote substring integrity                        |
| - Discards ungrounded LLM claims                            |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Evidence-Based Scoring & Recommendation Engine              |
| - Dynamic denominator weight normalization                  |
| - Insufficient data check (< 50 words or < 15s)             |
| - Prioritized coaching action generation                    |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| Persistence & Event Dispatch                                |
| - PostgreSQL atomic transaction (9 entities)                |
| - Redis Stream dispatch to 'analysis:events'                |
+-------------------------------------------------------------+
```

## 2. Ingestion & Boundary Guarantees
- **Temporal Alignment**: Preserves Step 07 millisecond start/end boundaries (`start_time_ms`, `end_time_ms`).
- **Speaker Attribution**: Uses `MeetingSpeaker.speaker_label` (`speaker_user_me`, `speaker_001`, etc.) to prevent speaker cross-talk contamination.
- **Idempotency**: Re-running analysis for a meeting updates existing sessions and clears prior provisional outputs to prevent duplicate records.
