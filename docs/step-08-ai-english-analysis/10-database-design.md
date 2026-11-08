# Step 08 — Database Schema & Data Models Specification

## 1. Relational Topology
Step 08 introduces nine dedicated PostgreSQL entities managing the lifecycle of AI English analysis:

```
+-------------------+       1:N       +----------------------+
|  analysis_sessions |---------------->| participant_analysis |
+-------------------+                 +----------------------+
          | 1:N                                  |
          v                                      +---> analysis_category_scores (1:N)
   analysis_events                               +---> grammar_issues (1:N)
                                                 +---> vocabulary_insights (1:N)
                                                 +---> fluency_metrics (1:N)
                                                 +---> communication_insights (1:N)
                                                 +---> improvement_recommendations (1:N)
```

## 2. Table Specifications
1. **analysis_sessions**: Tracks analysis job lifecycle (`queued`, `processing`, `completed`, `insufficient_data`, `failed`).
2. **participant_analysis**: Stores composite score, evidence coverage, confidence, and status per speaker.
3. **analysis_category_scores**: Category scores (grammar, vocabulary, fluency, sentence_structure, communication, contextual_language).
4. **grammar_issues**: Verified grammatical findings with rule name, original/corrected diffs, and severity.
5. **vocabulary_insights**: Lexical variety suggestions with business collocations and examples.
6. **fluency_metrics**: WPM, filler word rate, repetition rate, and pause telemetry.
7. **communication_insights**: Qualitative findings on active listening, tone, and clarity.
8. **improvement_recommendations**: Prioritized, actionable suggestions with before/after models.
9. **analysis_events**: Audit log tracking state transitions and error events.

## 3. Database Indexes & Constraints
- Multi-tenant foreign keys with cascading deletes.
- Unique constraint `uq_participant_analysis_session_speaker` on `(analysis_session_id, speaker_label)`.
- Unique constraint `uq_category_score_participant_cat` on `(participant_analysis_id, category)`.
- Index on `(meeting_id, status)` for fast status polling.
