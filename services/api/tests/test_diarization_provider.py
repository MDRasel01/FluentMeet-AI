"""
FluentMeet AI - Step 07 Test Suite: Diarization Provider
Specification: Step 07 - Section 5 (Speaker Diarization Pipeline)
"""

import pytest
import numpy as np
from app.transcription.diarization.pyannote import PyannoteDiarizationProvider

def generate_multi_pitch_audio(duration_s: float = 3.0, sample_rate: int = 16000) -> bytes:
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    # First half 250 Hz (low pitch speaker), second half 600 Hz (high pitch speaker)
    split = len(t) // 2
    part1 = (np.sin(2 * np.pi * 250.0 * t[:split]) * 14000).astype(np.int16)
    part2 = (np.sin(2 * np.pi * 600.0 * t[split:]) * 14000).astype(np.int16)
    return np.concatenate([part1, part2]).tobytes()

class TestDiarizationProvider:
    def test_source_0_always_attributes_to_local_user(self):
        provider = PyannoteDiarizationProvider()
        pcm = generate_multi_pitch_audio(duration_s=2.0)
        result = provider.diarize(pcm, sample_rate=16000, source_id=0)

        assert len(result.turns) == 1
        assert result.turns[0].speaker_label == "speaker_user_me"
        assert result.turns[0].start_ms == 0
        assert result.turns[0].end_ms >= 1900
        assert result.turns[0].confidence >= 0.95
        assert len(result.overlaps) == 0

    def test_silence_returns_empty_diarization(self):
        provider = PyannoteDiarizationProvider()
        silence_pcm = np.zeros(16000, dtype=np.int16).tobytes()
        result = provider.diarize(silence_pcm, sample_rate=16000, source_id=1)
        assert len(result.turns) == 0

    def test_source_1_differentiates_remote_speakers(self):
        provider = PyannoteDiarizationProvider(min_turn_duration_ms=200)
        pcm = generate_multi_pitch_audio(duration_s=3.0)
        result = provider.diarize(pcm, sample_rate=16000, source_id=1, num_speakers=2)

        assert len(result.turns) >= 2
        # Verify speaker labels follow naming standard
        for turn in result.turns:
            assert turn.speaker_label.startswith("speaker_")
            assert turn.duration_ms >= 200

    def test_detect_turn_overlaps(self):
        provider = PyannoteDiarizationProvider()
        from app.transcription.diarization.base import DiarizationSegment

        turns = [
            DiarizationSegment("speaker_001", start_ms=0, end_ms=1500, confidence=0.9),
            DiarizationSegment("speaker_002", start_ms=1000, end_ms=2500, confidence=0.9),
        ]
        overlaps = provider._detect_turn_overlaps(turns)
        assert len(overlaps) == 1
        assert overlaps[0].start_ms == 1000
        assert overlaps[0].end_ms == 1500
        assert overlaps[0].duration_ms == 500
        assert "speaker_001" in overlaps[0].overlapping_speakers
        assert "speaker_002" in overlaps[0].overlapping_speakers
