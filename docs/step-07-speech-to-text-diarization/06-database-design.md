# Step 07 — Multi-Tenant Database Design & Schema

## 1. Relational Entity Diagram

```mermaid
erDiagram
    MEETINGS ||--o{ MEETING_SPEAKERS : "has"
    MEETINGS ||--o{ TRANSCRIPT_SEGMENTS : "has"
    MEETINGS ||--o{ SPEAKER_TURNS : "has"
    MEETINGS ||--o{ SPEECH_OVERLAPS : "has"
    MEETINGS ||--o{ TRANSCRIPT_EVENTS : "emits"
    MEETING_SPEAKERS ||--o{ TRANSCRIPT_SEGMENTS : "attributes"
    MEETING_SPEAKERS ||--o{ SPEAKER_TURNS : "owns"
    TRANSCRIPT_SEGMENTS ||--o{ TRANSCRIPT_WORDS : "contains"

    MEETING_SPEAKERS {
        string id PK
        string meeting_id FK
        string speaker_label
        string display_name
        string user_id FK
        boolean is_identified
        float confidence_score
        int source_id
        json voice_embedding
        timestamp created_at
    }

    TRANSCRIPT_SEGMENTS {
        string id PK
        string meeting_id FK
        string speaker_id FK
        int source_id
        int start_time_ms
        int end_time_ms
        int duration_ms
        text text
        string language
        float confidence_score
        string status
        int revision_number
        string audio_segment_id FK
        json words_json
        timestamp created_at
    }

    TRANSCRIPT_WORDS {
        string id PK
        string transcript_segment_id FK
        string meeting_id FK
        string speaker_id FK
        string word
        int start_time_ms
        int end_time_ms
        float confidence_score
        int word_index
    }

    SPEAKER_TURNS {
        string id PK
        string meeting_id FK
        string speaker_id FK
        int source_id
        int start_time_ms
        int end_time_ms
        int duration_ms
        int turn_index
    }

    SPEECH_OVERLAPS {
        string id PK
        string meeting_id FK
        int start_time_ms
        int end_time_ms
        int duration_ms
        json overlapping_speaker_ids
        float confidence_score
    }

    TRANSCRIPT_EVENTS {
        string id PK
        string meeting_id FK
        string event_type
        json payload
        timestamp created_at
    }
```

## 2. Table Specifications & Indexing Strategy

### 2.1 `meeting_speakers`
- Unique constraint: `(meeting_id, speaker_label)`
- Indexes: `ix_meeting_speakers_meeting_id`, `ix_meeting_speakers_meeting_source`

### 2.2 `transcript_segments`
- Composite index: `(meeting_id, start_time_ms, end_time_ms)` for high-performance chronological queries.
- Status index: `(meeting_id, status)` for fast filtering of active or corrected revisions.

### 2.3 `transcript_words`
- Composite index: `(meeting_id, start_time_ms)` for instant seeking during audio playback.

### 2.4 `speaker_turns` & `speech_overlaps`
- Interval index: `(meeting_id, start_time_ms, end_time_ms)` for conversational pacing metrics.

## 3. Database Migrations
Step 07 tables are managed via Alembic revision `003_transcript_diarization.py` located at `services/api/migrations/versions/003_transcript_and_diarization_schema.py`.
