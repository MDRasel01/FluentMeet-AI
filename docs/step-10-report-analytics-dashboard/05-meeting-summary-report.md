# Step 10 — Meeting Summary Report Specification

**Module:** Aggregated Meeting Reports  
**Component:** `app.reports.builder.MeetingReportBuilder`  

---

## 1. Objective

The Meeting Summary Report provides team leaders, hiring managers, and enterprise executives with an aggregated, objective assessment of collective communication dynamics without losing individual participant accountability.

## 2. Structured Payload Schema

```json
{
  "metadata": {
    "meeting_id": "string",
    "title": "string",
    "meeting_date": "ISO8601",
    "report_type": "meeting_summary",
    "scoring_rubric_version": "1.0"
  },
  "summary_metrics": {
    "participant_count": 3,
    "total_duration_seconds": 320.5,
    "total_words": 1420,
    "average_overall_score": 82.3,
    "calibrated_participants_count": 3
  },
  "participants": [
    {
      "participant_id": "string",
      "speaker_label": "speaker_alice",
      "display_name": "Alice Smith",
      "overall_score": 85.0,
      "status_label": "Calibrated",
      "word_count": 720,
      "duration_seconds": 160.0,
      "talk_time_percentage": 49.9,
      "ielts_band": 7.5
    }
  ],
  "communication_balance": {
    "distribution": [
      { "speaker": "Alice Smith", "percentage": 49.9 },
      { "speaker": "Bob Jones", "percentage": 50.1 }
    ]
  },
  "highlights": [
    "Solid conversational English with opportunities for polish (Average: 82.3/100)."
  ],
  "areas_for_team_growth": [
    "4 grammatical structures identified for refinement across speakers."
  ],
  "disclaimers": {
    "summary": "Meeting summary is aggregated strictly from validated participant spoken contributions.",
    "ielts": "Educational practice estimate only. This is not an official IELTS score, certified assessment, or substitute for an IELTS examiner."
  }
}
```

## 3. Communication Balance Metrics
- Computes each speaker's share of total vocal speaking duration:
  $$\text{Talk Time \%} = \text{round}\left(\frac{\text{Duration}_{\text{speaker}}}{\text{Total Vocal Duration}} \times 100, 1\right)$$
- Highlights turn-taking and dominant speaker tendencies.
