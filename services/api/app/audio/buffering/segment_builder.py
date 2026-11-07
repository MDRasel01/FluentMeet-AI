"""
FluentMeet AI - Audio Segment Builder
Specification: Step 06 - Section 12.2
"""

import hashlib
import uuid
from dataclasses import dataclass
from typing import List
from app.audio.protocol import AudioPacket

@dataclass
class CompletedSegment:
    segment_id: str
    meeting_id: str
    stream_id: str
    source_id: int
    start_timestamp: float
    end_timestamp: float
    first_sequence: int
    last_sequence: int
    sample_rate: int
    channels: int
    sample_count: int
    duration_ms: int
    checksum: str
    pcm_bytes: bytes

class SegmentBuilder:
    @staticmethod
    def build_segment(
        meeting_id: str,
        stream_id: str,
        source_id: int,
        chunks: List[AudioPacket]
    ) -> CompletedSegment:
        if not chunks:
            raise ValueError("Cannot build an audio segment from empty chunks list")

        pcm_combined = b"".join(chunk.pcm_payload for chunk in chunks)
        total_samples = sum(chunk.sample_count for chunk in chunks)
        sample_rate = chunks[0].sample_rate
        channels = chunks[0].channels

        start_ts = chunks[0].session_relative_timestamp_ms
        end_ts = chunks[-1].session_relative_timestamp_ms
        first_seq = chunks[0].sequence_number
        last_seq = chunks[-1].sequence_number

        duration_ms = int((total_samples / sample_rate) * 1000)
        sha256 = hashlib.sha256(pcm_combined).hexdigest()
        segment_id = str(uuid.uuid4())

        return CompletedSegment(
            segment_id=segment_id,
            meeting_id=meeting_id,
            stream_id=stream_id,
            source_id=source_id,
            start_timestamp=start_ts,
            end_timestamp=end_ts,
            first_sequence=first_seq,
            last_sequence=last_seq,
            sample_rate=sample_rate,
            channels=channels,
            sample_count=total_samples,
            duration_ms=duration_ms,
            checksum=sha256,
            pcm_bytes=pcm_combined,
        )
