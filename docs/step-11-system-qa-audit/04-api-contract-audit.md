# Step 11: 04 — API Contract & Endpoint Audit

**Module:** API Contract & Schema Verification  
**Step:** 11 of 12  
**Protocol:** REST (HTTP/2) & Real-Time (WSS Binary/JSON)  

---

## 1. REST Endpoint Inventory & Contract Mapping

All API endpoints reside under `/api/v1` and strictly return structured envelopes adhering to the standard schema:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Authentication (`/api/v1/auth`)
- `POST /register`: Registers user, hashes password with bcrypt, emits verification token.
- `POST /login`: Authenticates user credentials, returns access token (15m expiry) and refresh token (7d expiry).
- `POST /refresh`: Validates refresh token, rotates tokens, invalidates old token.
- `POST /logout`: Invalidates active auth session.

### Meetings (`/api/v1/meetings`)
- `POST /`: Creates a meeting record associated with the caller's `organization_id`.
- `GET /`: Lists paginated meetings with tenant isolation.
- `GET /{meeting_id}`: Retrieves meeting details, verifying tenant ownership.

### Audio & Streaming (`/ws/v1/sessions/{session_id}`, `/api/v1/audio`)
- `WSS /ws/v1/sessions/{session_id}`: Binary PCM streaming socket.
  - Handshake requires valid JWT token in production (`DEF-001`).
  - Origin must match Chrome Extension or allowed domains.
  - Acknowledges packets with two-tier ACK (L1 memory, L2 disk).
- `POST /api/v1/audio/meetings/{meeting_id}/flush`: Flushes audio buffer to storage.

### Transcription & Diarization (`/api/v1/transcription`)
- `GET /meetings/{meeting_id}/transcript`: Returns diarized speaker segments and word-level timestamps.

### Linguistic Analysis (`/api/v1/analysis`)
- `POST /meetings/{meeting_id}/analyze`: Triggers Step 08 Gemini 2.5 Flash English analysis.
- `GET /meetings/{meeting_id}/analysis`: Retrieves structured grammar, vocabulary, fluency, and communication findings.

### Pronunciation & IELTS Assessment (`/api/v1/pronunciation`)
- `POST /meetings/{meeting_id}/assess`: Triggers Step 09 acoustic alignment and IELTS band estimation.
- `GET /meetings/{meeting_id}/assessment`: Retrieves pronunciation scores, phoneme errors, prosody metrics, and IELTS practice band with mandatory disclaimer.

### Reports & Dashboard (`/api/v1/reports`, `/api/v1/dashboard`)
- `POST /api/v1/reports/generate`: Generates immutable `meeting_summary` and `individual_participant` snapshots.
- `GET /api/v1/reports/{report_id}`: Fetches report snapshot payload.
- `GET /api/v1/reports/participant/{participant_id}/history`: Long-term trajectory tracking.
- `POST /api/v1/reports/{report_id}/export/csv`: Generates CSV export with formula injection defense.
- `POST /api/v1/reports/{report_id}/export/html`: Generates print-ready HTML view with SHA-256 integrity hash.
- `GET /api/v1/dashboard/summary`: High-level aggregated KPIs for authenticated organization.
- `GET /api/v1/dashboard/trends`: Multi-meeting historical skill score trends.

