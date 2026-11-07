# Step 07 — REST & WebSocket API Contract Specification

## 1. REST Endpoints

### 1.1 List Meeting Transcripts
`GET /api/v1/meetings/{meeting_id}/transcripts`
- **Query Parameters:**
  - `speaker_id` (string, optional): Filter by speaker UUID.
  - `status` (string, optional): `partial`, `provisional`, `final`, `corrected`.
  - `start_ms` (integer, optional): Min millisecond bound.
  - `end_ms` (integer, optional): Max millisecond bound.
  - `limit` (integer, default 200).
- **Response 200 OK:**
```json
{
  "success": true,
  "data": [
    {
      "id": "seg-uuid",
      "meeting_id": "meet-uuid",
      "speaker_id": "spk-uuid",
      "speaker_label": "speaker_user_me",
      "speaker_name": "You (Host)",
      "source_id": 0,
      "start_time_ms": 0,
      "end_time_ms": 3200,
      "duration_ms": 3200,
      "text": "Welcome to our Sprint Planning.",
      "language": "en",
      "confidence_score": 0.98,
      "status": "final",
      "revision_number": 1,
      "words": [
        {
          "word": "Welcome",
          "start_time_ms": 0,
          "end_time_ms": 500,
          "confidence_score": 0.99
        }
      ]
    }
  ]
}
```

### 1.2 Get Transcript Segment
`GET /api/v1/meetings/{meeting_id}/transcripts/{segment_id}`

### 1.3 Manual Transcript Correction
`PATCH /api/v1/meetings/{meeting_id}/transcripts/{segment_id}`
- **Request Body:**
```json
{
  "text": "Welcome to our Q3 Sprint Planning.",
  "speaker_id": "spk-uuid-optional"
}
```
- **Response 200 OK:** Returns corrected segment with status `"corrected"` and incremented `revision_number`.

### 1.4 List Meeting Speakers
`GET /api/v1/meetings/{meeting_id}/speakers`

### 1.5 Rename / Update Speaker
`PATCH /api/v1/meetings/{meeting_id}/speakers/{speaker_id}`
- **Request Body:**
```json
{
  "display_name": "Michael Scott",
  "participant_id": "optional-participant-uuid"
}
```

### 1.6 List Speech Overlaps
`GET /api/v1/meetings/{meeting_id}/overlaps`

---

## 2. WebSocket Protocols
- Real-Time Endpoint: `ws://host/ws/meetings/{meeting_id}/transcripts?token={jwt}`
- Supported inbound messages:
  - `{"type": "subscribe_transcripts", "meetingId": "..."}`
  - `{"type": "ping"}`
- Inbound broadcast events:
  - `transcript.partial`: streaming active words
  - `transcript.final`: finalized sentence block
  - `transcript.corrected`: human update notification
  - `speaker.detected`: newly identified speaker
  - `speaker.updated`: updated name or label
  - `speaker.overlap`: cross-talk interval warning
