# Observability, Telemetry & Monitoring

## 1. Structured Logging & Trace Context

All logging across the API, WebSocket server, and consumer workers outputs JSON-formatted log lines conforming to production log ingestion standards (Elasticsearch / Datadog / CloudWatch):

```json
{
  "timestamp": "2026-11-07T06:15:00.120Z",
  "level": "INFO",
  "service": "fluentmeet-api",
  "logger": "websocket.audio",
  "session_id": "meet-614ef-908a",
  "source_id": 0,
  "sequence_number": 105,
  "message": "Ingested binary chunk successfully"
}
```

---

## 2. Key Audio Health Metrics

| Metric Name | Type | Description | Target / SLA |
| :--- | :--- | :--- | :--- |
| `audio.chunks.received_total` | Counter | Total chunks received per source | Monotonic increase |
| `audio.chunks.rejected_total` | Counter | Invalid or duplicate chunks rejected | $< 0.1\%$ |
| `audio.clock_drift_ms` | Gauge | Instantaneous clock drift between browser and server | $< 200 \text{ ms}$ |
| `audio.buffer.overflow_total` | Counter | Number of buffer overflow / backpressure events | $0$ under normal load |
| `audio.segments.persisted_total`| Counter | Number of segments written to durable storage | Matches expected duration |
| `audio.worker.dlq_total` | Counter | Messages routed to dead-letter stream | $0$ (Alert threshold $\ge 1$) |

---

## 3. Sentry & Error Tracing

* Unhandled exceptions within WebSocket loops or worker consumers automatically capture stack traces and send them to Sentry (when `settings.SENTRY_DSN` is configured).
* Context tags: `meeting_id`, `organization_id`, `source_id`, `sequence_number`.
