# Step 09 — REST API Contract & Specification

## 1. Endpoints Overview

Base path: `/api/v1`

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/meetings/{meeting_id}/pronunciation` | Trigger or fetch assessment for meeting participant(s). |
| `POST` | `/pronunciation/assessments` | Trigger assessment with meeting ID in payload body. |
| `GET` | `/meetings/{meeting_id}/pronunciation` | List all pronunciation assessments for a meeting. |
| `GET` | `/pronunciation/assessments/{id}` | Retrieve top-level assessment details, status, and summary. |
| `GET` | `/pronunciation/assessments/{id}/words` | Retrieve granular word-level acoustic scores and phonemes. |
| `GET` | `/pronunciation/assessments/{id}/prosody` | Retrieve pitch contour, stress scores, WPM, and pauses. |
| `GET` | `/pronunciation/assessments/{id}/recommendations` | Retrieve actionable pronunciation drills and minimal pairs. |
| `GET` | `/pronunciation/assessments/{id}/ielts` | Retrieve 4-dimension IELTS practice estimate and disclaimer. |
| `POST` | `/pronunciation/assessments/{id}/retry` | Re-run assessment with `force_reassess=True`. |

---

## 2. Selected Request & Response Payloads

### 2.1 Trigger Assessment Request
```json
POST /api/v1/meetings/550e8400-e29b-41d4-a716-446655440000/pronunciation
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "speaker_id": "spk-12345",
  "force_reassess": false
}
```

### 2.2 IELTS Practice Estimate Response
```json
GET /api/v1/pronunciation/assessments/asmt-99999/ielts
HTTP/1.1 200 OK

{
  "success": true,
  "data": {
    "id": "ielts-1001",
    "assessment_id": "asmt-99999",
    "participant_id": "part-88888",
    "fluency_coherence_estimate": 7.0,
    "lexical_resource_estimate": 7.0,
    "grammatical_accuracy_estimate": 7.5,
    "pronunciation_estimate": 7.5,
    "overall_practice_estimate": 7.5,
    "qualitative_band_descriptor": "Good Professional Communicator (Band 7.5 Practice Level)",
    "rubric_version": "1.0-qualitative-calibrated",
    "confidence": 0.95,
    "evidence_coverage": 1.0,
    "assessment_status": "completed",
    "disclaimer_version": "1.0",
    "disclaimer_text": "Educational practice estimate only. This is not an official IELTS score, certified assessment, or substitute for an IELTS examiner."
  },
  "error": null,
  "message": null
}
```

