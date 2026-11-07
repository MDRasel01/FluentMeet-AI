# System Architecture — Step 06 Audio Ingestion & Streaming Backend

## 1. Architectural Overview

The Step 06 Audio Ingestion & Processing backend is engineered for ultra-reliable, high-concurrency real-time stream ingestion. It decouples high-frequency network I/O from storage and downstream AI compute tasks using memory-bounded buffering, transactional persistence, and event-driven worker distribution.

```mermaid
flowchart TD
    subgraph Client["Chrome Extension (Step 05)"]
        Tab["Remote Tab Audio (Source 0)"]
        Mic["Local Mic Audio (Source 1)"]
        Encoder["AudioEncoder (Binary Framing)"]
        WSClient["WebSocket Client"]
        Tab --> Encoder
        Mic --> Encoder
        Encoder --> WSClient
    end

    subgraph FastAPIService["FastAPI Ingestion Gateway"]
        WSEndpoint["WebSocket Endpoint (/ws/meetings/{id}/audio)"]
        Proto["Binary Audio Protocol Decoder"]
        Val["Audio Validator (Format & Quality)"]
        SeqSync["Sequence Manager & Clock Drift Tracker"]
        BufMgr["Audio Buffer Manager (Source Isolated)"]
        TwoTier["ACK Dispatcher"]
        
        WSClient -->|Binary Frames| WSEndpoint
        WSEndpoint --> Proto
        Proto --> Val
        Val --> SeqSync
        SeqSync --> BufMgr
        SeqSync -.->|Level 1: audio_received| TwoTier
        TwoTier -.->|JSON ACK| WSClient
    end

    subgraph Persistence["Storage & Database Tier"]
        ObjStore["Private Object Storage (PCM S16LE Segments)"]
        Postgres[("PostgreSQL Database (Audio Metadata & Outbox)")]
        RedisBus[("Redis Streams (audio:segment:created)")]
        
        BufMgr -->|Flush 3s Segment| ObjStore
        BufMgr -->|Commit Segment & Outbox| Postgres
        BufMgr -->|XADD Event| RedisBus
        BufMgr -.->|Level 2: audio_persisted| TwoTier
    end

    subgraph WorkerTier["Async Consumer Workers"]
        Consumer["AudioStreamConsumer (Group: audio_workers)"]
        DLQ["Dead-Letter Stream (audio:dead-letter)"]
        Downstream["Step 07 AI Pipeline (ASR & Diarization)"]
        
        RedisBus -->|XREADGROUP| Consumer
        Consumer -->|Verify Storage & Update DB| Postgres
        Consumer -->|XACK| RedisBus
        Consumer -.->|Max Retries Exceeded| DLQ
        Consumer --> Downstream
    end
```

---

## 2. Audio Pipeline Separation

A core foundational principle of FluentMeet AI is the absolute separation of the two independent audio sources:
* **Pipeline A (`source_id = 0`):** Remote Meeting Audio captured from the browser tab via `chrome.tabCapture.getMediaStreamId()`. Represents all remote speakers in the Google Meet, Teams, or Zoom session.
* **Pipeline B (`source_id = 1`):** Local Microphone Audio captured from the user's headset or microphone via `navigator.mediaDevices.getUserMedia()`. Represents the single coached learner.

### Isolation Rules
1. **No Mixed Buffers:** Buffering occurs inside separate dictionaries indexed by `source_id`. Under no circumstances are samples summed, interleaved, or shared across source buffers.
2. **Independent Monotonic Sequences:** Each source tracks its own sequence counter starting at 1. Chunk drops or gaps in Source 0 do not impact Source 1 sequence evaluation.
3. **Dedicated Object Keys:** Storage paths explicitly segregate sources:
   `.../sources/0/segments/{id}.pcm` vs `.../sources/1/segments/{id}.pcm`.
4. **Distinct AI Targets in Step 07:** Downstream models perform speaker diarization on Pipeline A, while Pipeline B undergoes high-fidelity phonetic pronunciation, grammar, and vocabulary scoring.

---

## 3. End-to-End Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as Chrome Extension
    participant WS as FastAPI WebSocket
    participant Ingest as Central Ingestion Service
    participant Storage as Private Object Storage
    participant DB as PostgreSQL
    participant Redis as Redis Streams
    participant Worker as Background Worker

    User->>WS: Handshake (Token + Origin + Session ID)
    WS-->>User: connection_ack (ready)

    loop Every 100ms
        User->>WS: Binary Frame (23+N byte header + PCM)
        WS->>Ingest: ingest_binary_packet(bytes)
        Ingest->>Ingest: Decode framing & validate format
        Ingest->>Ingest: Sequence check & clock drift calculation
        Ingest-->>WS: Level 1: audio_received (status: accepted)
        WS-->>User: {"type": "audio_received", "seq": 1, ...}

        alt Target Segment Duration Reached (3000ms)
            Ingest->>Storage: put_object(key, pcm_bytes, expected_sha256)
            Ingest->>DB: INSERT audio_segment, quality_metrics, outbox_event
            Ingest->>Redis: XADD audio:segment:created
            Ingest-->>WS: Level 2: audio_persisted (segmentId, checksum, key)
            WS-->>User: {"type": "audio_persisted", "segmentId": "...", ...}
        end
    end

    Redis->>Worker: XREADGROUP (audio_segment_created event)
    Worker->>Storage: exists(storage_key)
    Worker->>DB: UPDATE audio_segments SET processing_status='ready'
    Worker->>Redis: XACK (audio:segment:created, msg_id)

    User->>WS: JSON session_stop
    WS->>Ingest: flush_remaining_audio()
    Ingest->>Storage: put_object(partial_segment)
    Ingest->>DB: INSERT final segment & commit
    Ingest-->>WS: Level 2: audio_persisted
    WS-->>User: {"type": "session_completed", "flushed_segments": 1}
    WS->>WS: Clean connection close
```
