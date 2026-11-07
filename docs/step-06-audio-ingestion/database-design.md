# Database Design & Transactional Outbox Pattern

## 1. Entity-Relationship Schema

The Step 06 persistence layer is designed around 7 core tables mapped in SQLAlchemy (`app/models/audio.py`):

```mermaid
erDiagram
    MEETINGS ||--o{ AUDIO_STREAMS : has
    AUDIO_STREAMS ||--o{ AUDIO_SEGMENTS : contains
    AUDIO_STREAMS ||--o{ AUDIO_STREAM_GAPS : tracks
    AUDIO_SEGMENTS ||--|| AUDIO_QUALITY_METRICS : analyzes
    ORGANIZATIONS ||--o{ AUDIO_USAGE_RECORDS : bills
    AUDIO_OUTBOX_EVENTS ||--|| AUDIO_SEGMENTS : dispatches

    AUDIO_STREAMS {
        string id PK
        string meeting_id FK
        string organization_id FK
        string user_id FK
        int source_id
        string stream_id
        string encoding
        int sample_rate
        int channels
        string stream_status
        bigint last_sequence
        float last_timestamp
        datetime started_at
        datetime ended_at
    }

    AUDIO_SEGMENTS {
        string id PK
        string meeting_id FK
        string stream_id
        int source_id
        float start_timestamp
        float end_timestamp
        bigint first_sequence
        bigint last_sequence
        int sample_rate
        int channels
        string encoding
        int sample_count
        int duration_ms
        string checksum
        string storage_key
        string storage_status
        string processing_status
    }

    AUDIO_QUALITY_METRICS {
        string id PK
        string segment_id FK
        float rms_level
        float peak_amplitude
        float clipping_ratio
        float silence_ratio
        int invalid_sample_count
        int duration_ms
    }

    AUDIO_STREAM_GAPS {
        string id PK
        string stream_id FK
        int source_id
        bigint missing_sequence_start
        bigint missing_sequence_end
        boolean gap_resolved
    }

    AUDIO_USAGE_RECORDS {
        string id PK
        string organization_id FK
        string user_id FK
        string meeting_id FK
        int source_id
        bigint audio_duration_ms
        bigint storage_bytes
        bigint processed_bytes
        string billing_period
    }

    AUDIO_OUTBOX_EVENTS {
        string id PK
        string event_type
        string aggregate_id
        json payload
        datetime published_at
    }
```

---

## 2. Transactional Outbox Pattern

To prevent distributed dual-write inconsistencies between PostgreSQL and Redis Streams:
1. When an audio segment completes, `db.add(db_segment)` and `db.add(outbox_event)` occur in the **same database transaction**.
2. If the process terminates before publishing to Redis:
   * The un-published event remains in `audio_outbox_events` with `published_at IS NULL`.
   * A periodic outbox relay worker scans for pending outbox events and publishes them to Redis.
3. Once published, `published_at` is stamped.
