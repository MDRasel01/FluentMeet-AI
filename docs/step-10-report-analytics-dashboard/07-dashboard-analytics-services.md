# Step 10 — Dashboard Analytics Services Specification

**Module:** Dashboard KPIs & Feeds  
**Component:** `app.reports.analytics.DashboardAnalyticsService`  

---

## 1. Overview

The Dashboard Analytics Service queries stored immutable snapshots to deliver low-latency KPIs, trend timelines, and recent meeting status feeds without recomputing raw audio or linguistic analysis.

## 2. API Services

### 2.1 Executive Summary (`GET /api/v1/dashboard/summary`)
Returns aggregated KPI cards for the current user/tenant:
- `total_meetings_analyzed`: Count of distinct meetings with completed reports.
- `total_speaking_hours`: Cumulative duration of vocal speech in hours.
- `average_english_score`: Arithmetic mean of calibrated scores across all meetings.
- `ielts_average_band`: Average IELTS practice band estimate.
- `top_recurring_grammar_errors`: Top 5 grammatical mistakes across meetings.
- `top_vocabulary_enhancement_areas`: Overused words and vocabulary upgrade targets.
- `active_participants_count`: Distinct speakers evaluated.

### 2.2 Historical Trends Series (`GET /api/v1/dashboard/trends`)
Returns chronological time series suitable for charting:
- `dates`: Formatted meeting dates (`"Oct 24"`, `"Nov 02"`, etc.).
- `overall_scores`: Score progression.
- `grammar_scores`, `vocabulary_scores`, `fluency_scores`, `pronunciation_scores`.

### 2.3 Recent Meetings Feed (`GET /api/v1/dashboard/recent-meetings`)
Returns recent meeting entries with title, date, duration, participant count, average score, report snapshot ID, and completion status.
