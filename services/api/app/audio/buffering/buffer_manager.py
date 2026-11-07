"""
FluentMeet AI - Audio Buffer Manager & Backpressure Engine
Specification: Step 06 - Section 12
"""

from typing import Dict, List, Optional
from app.audio.protocol import AudioPacket
from app.audio.buffering.segment_builder import CompletedSegment, SegmentBuilder

class BufferOverflowError(Exception):
    """Raised when an audio buffer exceeds its configured memory boundaries."""
    pass

class AudioBufferManager:
    def __init__(
        self,
        target_segment_duration_ms: int = 3000,
        max_buffer_chunks: int = 100,
        sample_rate: int = 16000
    ):
        self.target_segment_duration_ms = target_segment_duration_ms
        self.max_buffer_chunks = max_buffer_chunks
        self.sample_rate = sample_rate

        # source_id -> list of AudioPacket chunks
        self.buffers: Dict[int, List[AudioPacket]] = {}
        # source_id -> cumulative buffered samples
        self.buffered_samples: Dict[int, int] = {}

    def push_chunk(self, chunk: AudioPacket) -> Optional[CompletedSegment]:
        source_id = chunk.source_id
        if source_id not in self.buffers:
            self.buffers[source_id] = []
            self.buffered_samples[source_id] = 0

        # Enforce memory boundary
        if len(self.buffers[source_id]) >= self.max_buffer_chunks:
            raise BufferOverflowError(
                f"Audio buffer for source {source_id} exceeded maximum limit of {self.max_buffer_chunks} chunks."
            )

        self.buffers[source_id].append(chunk)
        self.buffered_samples[source_id] += chunk.sample_count

        current_duration_ms = (self.buffered_samples[source_id] / self.sample_rate) * 1000

        # Check if segment duration target reached
        if current_duration_ms >= self.target_segment_duration_ms:
            return self._flush_source(source_id)

        return None

    def flush_source(self, source_id: int) -> Optional[CompletedSegment]:
        return self._flush_source(source_id)

    def flush_all(self) -> List[CompletedSegment]:
        segments = []
        for source_id in list(self.buffers.keys()):
            seg = self._flush_source(source_id)
            if seg:
                segments.append(seg)
        return segments

    def _flush_source(self, source_id: int) -> Optional[CompletedSegment]:
        chunks = self.buffers.get(source_id, [])
        if not chunks:
            return None

        segment = SegmentBuilder.build_segment(
            meeting_id=chunks[0].meeting_id,
            stream_id=f"stream-{source_id}",
            source_id=source_id,
            chunks=chunks
        )

        self.buffers[source_id] = []
        self.buffered_samples[source_id] = 0
        return segment

    def is_backpressure_required(self, source_id: int) -> bool:
        chunks = self.buffers.get(source_id, [])
        return len(chunks) >= (self.max_buffer_chunks * 0.8)
