# Step 08 — REST API Contract Specification

## 1. Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/meetings/{id}/analysis` | Trigger/retrieve idempotent meeting analysis | Yes |
| `GET` | `/api/v1/analysis/{id}/status` | Poll lightweight analysis session status | Yes |
| `GET` | `/api/v1/analysis/{id}` | Get session details and participant score summaries | Yes |
| `GET` | `/api/v1/analysis/{id}/participants/{pid}` | Get detailed report (grammar, vocab, fluency, recs) | Yes |
| `GET` | `/api/v1/participants/{speaker}/progress` | Chronological multi-meeting progress tracking | Yes |
| `GET` | `/api/v1/participants/{speaker}/recommendations` | Active coaching recommendations for speaker | Yes |

## 2. Request & Response Samples

### Trigger Analysis (`POST /api/v1/meetings/{id}/analysis`)
```json
// Request Body
{
  "force_reanalyze": false
}

// Response Body (200 OK)
{
  "success": true,
  "data": {
    "id": "2be4d4cb-5314-4faa-b23d-57a3499d3780",
    "meeting_id": "da04fe14-a866-4240-b114-ab32a2e1b182",
    "status": "completed",
    "requested_at": "2026-11-08T23:00:00Z",
    "started_at": "2026-11-08T23:00:01Z",
    "completed_at": "2026-11-08T23:00:04Z",
    "participants": [
      {
        "id": "p-101",
        "speaker_label": "speaker_user_me",
        "overall_score": 87.5,
        "score_status": "available",
        "evidence_coverage": 1.0,
        "category_scores": [
          {"category": "grammar", "score": 88.0, "status": "available"},
          {"category": "vocabulary", "score": 85.0, "status": "available"},
          {"category": "fluency", "score": 90.0, "status": "available"},
          {"category": "sentence_structure", "score": 84.0, "status": "available"},
          {"category": "communication", "score": 89.0, "status": "available"},
          {"category": "contextual_language", "score": 90.0, "status": "available"}
        ]
      }
    ]
  }
}
```
