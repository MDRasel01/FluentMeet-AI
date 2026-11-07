# Step 07 — Security, Data Privacy & Tenant Isolation

## 1. Multi-Tenant Authorization Boundaries
- Every database query in `services/api/app/api/v1/transcripts.py` verifies meeting ownership via `_verify_meeting_access`.
- Cross-tenant access attempts immediately fail with `403 FORBIDDEN` or `404 NOT FOUND`.
- Foreign key cascading constraints guarantee that deleting a meeting permanently purges all associated transcript segments, words, speaker labels, and overlaps.

## 2. PII Protection & Ground-Truth Honesty
- **No Identity Guessing:** The pipeline never fabricates personal names from voice characteristics. Remote speakers are strictly assigned synthetic meeting-scoped identifiers (`speaker_001`, `speaker_002`) until the meeting owner explicitly renames them.
- **No Fabricated Confidence:** If confidence metrics are uncalibrated or missing, the database records `null` rather than a misleading artificial probability score.
- **Audio Minimization:** Temporary intermediate wav files or resampled buffers are processed entirely in-memory using NumPy arrays, preventing residual audio artifacts on disk.
