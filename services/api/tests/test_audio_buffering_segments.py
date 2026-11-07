"""
FluentMeet AI - Step 06 Test Suite: Audio Buffering & Segment Building
Specification: Step 06 - Section 12, 13 & 21 (REQ-ING-010, REQ-ING-011)
"""

import pytest
import numpy as np
from app.audio.protocol import AudioPacket
from app.audio.buffering.buffer_manager import AudioBufferManager, BufferOverflowError

def make_chunk(source_id: int, seq: int, ts: float, duration_ms: int = 1000) -> AudioPacket:
    sample_count = int(16000 * (duration_ms / 1000.0))
    # Synthetic tone
    t = np.linspace(0, duration_ms / 1000.0, sample_count, endpoint=False)
    pcm = (np.sin(2 * np.pi * 440 * t) * 10000).astype(np.int16).tobytes()
    return AudioPacket(
        version=1,
        source_id=source_id,
        sequence_number=seq,
        session_relative_timestamp_ms=ts,
        sample_rate=16000,
        channels=1,
        encoding=1,
        sample_count=sample_count,
        meeting_id="meeting-test-1",
        pcm_payload=pcm,
    )

class TestAudioBufferingAndSegments:
    def test_strict_source_separation(self):
        buf = AudioBufferManager(target_segment_duration_ms=3000)

        # Feed 2000ms to source 0 and 1000ms to source 1
        buf.push_chunk(make_chunk(source_id=0, seq=1, ts=0.0, duration_ms=2000))
        buf.push_chunk(make_chunk(source_id=1, seq=1, ts=0.0, duration_ms=1000))

        # Check internal buffer queues are separated
        assert len(buf.buffers[0]) == 1
        assert len(buf.buffers[1]) == 1
        assert buf.buffered_samples[0] == 32000
        assert buf.buffered_samples[1] == 16000

    def test_target_duration_segment_flush(self):
        buf = AudioBufferManager(target_segment_duration_ms=3000)

        # Push 1000ms chunks to source 0
        seg1 = buf.push_chunk(make_chunk(source_id=0, seq=1, ts=0.0, duration_ms=1000))
        assert seg1 is None

        seg2 = buf.push_chunk(make_chunk(source_id=0, seq=2, ts=1000.0, duration_ms=1000))
        assert seg2 is None

        seg3 = buf.push_chunk(make_chunk(source_id=0, seq=3, ts=2000.0, duration_ms=1000))
        # Now 3000ms reached, must produce completed segment
        assert seg3 is not None
        assert seg3.source_id == 0
        assert seg3.duration_ms == 3000
        assert seg3.sample_count == 48000
        assert seg3.first_sequence == 1
        assert seg3.last_sequence == 3
        assert len(seg3.pcm_bytes) == 48000 * 2
        assert len(seg3.checksum) == 64  # SHA256 hex string

    def test_flush_remaining_audio(self):
        buf = AudioBufferManager(target_segment_duration_ms=3000)
        # Push 1500ms to source 0 and 1200ms to source 1
        buf.push_chunk(make_chunk(source_id=0, seq=1, ts=0.0, duration_ms=1500))
        buf.push_chunk(make_chunk(source_id=1, seq=1, ts=0.0, duration_ms=1200))

        remaining = buf.flush_all()
        assert len(remaining) == 2

        s0 = next(s for s in remaining if s.source_id == 0)
        s1 = next(s for s in remaining if s.source_id == 1)

        assert s0.duration_ms == 1500
        assert s1.duration_ms == 1200

    def test_buffer_overflow_backpressure(self):
        # Buffer with max capacity of 5 chunks
        buf = AudioBufferManager(target_segment_duration_ms=100000, max_buffer_chunks=5)

        for i in range(5):
            buf.push_chunk(make_chunk(source_id=0, seq=i+1, ts=i*100.0, duration_ms=100))

        # 6th chunk should trigger BufferOverflowError
        with pytest.raises(BufferOverflowError):
            buf.push_chunk(make_chunk(source_id=0, seq=6, ts=500.0, duration_ms=100))
