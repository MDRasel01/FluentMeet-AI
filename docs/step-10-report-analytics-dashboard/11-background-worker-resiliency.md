# Step 10 — Background Worker Architecture & Resiliency

**Module:** Background Queue & Stream Consumer  
**Component:** `app.consumers.report_consumer.ReportStreamConsumer`  

---

## 1. Stream Architecture

The background report worker consumes jobs from Redis Streams to asynchronously aggregate, validate, and persist immutable reports without blocking client HTTP request loops.

- **Stream Name:** `report:jobs`
- **Consumer Group:** `report_workers`
- **Dead Letter Queue (DLQ):** `report:jobs:dlq`
- **Max Retries:** 3 attempts
- **Pending Idle Reclaim:** 60,000 ms

## 2. Job Payload Contract

```json
{
  "meeting_id": "meet-uuid",
  "user_id": "user-uuid",
  "tenant_id": "org-uuid",
  "force_regenerate": false,
  "scoring_rubric_version": "1.0"
}
```

## 3. Failure Handling & DLQ Isolation

1. When an exception occurs during report processing:
   - Increments `retry_count` in message payload.
   - If `retry_count < 3`: republishes to `report:jobs` and ACKs original message.
   - If `retry_count >= 3`: moves message to `report:jobs:dlq` with `error_reason`, timestamp, and `original_message_id`, then ACKs original message.
