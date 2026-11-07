# Buffer Management & Backpressure Controls

## 1. Memory-Bounded Ring Buffers

To prevent unbounded memory growth during high-concurrency ingestion or network stalling, `AudioBufferManager` maintains bounded chunk queues per source.

### Configuration Parameters
* `target_segment_duration_ms`: Target duration before flushing an assembled segment (default: **3000 ms**).
* `max_buffer_chunks`: Hard limit of chunks buffered in RAM per source before triggering backpressure (default: **100 chunks**, representing ~10 seconds of 100ms chunks).
* `sample_rate`: Target rate (16,000 Hz).

---

## 2. Segment Assembling Rules

Chunks accumulate in chronological sequence within `AudioBufferManager.buffers[source_id]`.
* Each incoming chunk adds its samples to `buffered_samples[source_id]`.
* Current duration is evaluated:
  $$D_{\text{current}} = \left( \frac{\text{buffered\_samples}}{16000} \right) \times 1000 \quad [\text{ms}]$$
* When $D_{\text{current}} \ge 3000 \text{ ms}$, the buffer is drained and passed to `SegmentBuilder.build_segment()`:
  1. Combines raw PCM bytes: $B_{\text{segment}} = \text{concat}(B_1, B_2, \dots, B_m)$.
  2. Generates SHA-256 checksum over $B_{\text{segment}}$.
  3. Records `first_sequence` and `last_sequence`.
  4. Returns a `CompletedSegment` for durable persistence.

---

## 3. Backpressure & Overflow Protection

If the backend storage layer or database slows down and chunks arrive faster than they can be drained:
1. `len(buffers[source_id]) >= max_buffer_chunks` triggers `BufferOverflowError`.
2. The WebSocket endpoint catches `BufferOverflowError` and sends a backpressure notice:
   ```json
   {
     "type": "audio_backpressure",
     "code": "BUFFER_OVERFLOW",
     "message": "Audio buffer for source 0 exceeded maximum limit of 100 chunks.",
     "session_id": "meet-test-123"
   }
   ```
3. The Chrome Extension slows down chunk transmission or throttles capture frame dispatch until storage catches up.
