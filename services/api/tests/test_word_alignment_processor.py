"""
FluentMeet AI - Step 09 Test Suite: Word-Level Audio Alignment Processor
Specification: Step 09 - Section 7
"""

import pytest
import numpy as np
from app.pronunciation.alignment.word_aligner import WordAlignmentProcessor, AlignedWordAudio


class DummyWord:
    def __init__(self, word: str, start_time_ms: int, end_time_ms: int, confidence: float = 0.95):
        self.word = word
        self.start_time_ms = start_time_ms
        self.end_time_ms = end_time_ms
        self.confidence_score = confidence


class TestWordAlignmentProcessor:
    def test_clean_word_token(self):
        aligner = WordAlignmentProcessor()
        assert aligner.clean_word_token("think,") == "think"
        assert aligner.clean_word_token('"architecture"') == "architecture"
        assert aligner.clean_word_token("don't") == "don't"
        assert aligner.clean_word_token("   ") == ""

    def test_align_words_within_segment_boundaries(self):
        """Aligns words cleanly within segment timestamp bounds and extracts PCM slices."""
        aligner = WordAlignmentProcessor()
        sample_rate = 16000
        # 2 seconds synthetic PCM
        synth_pcm = (np.ones(sample_rate * 2, dtype=np.int16) * 500).tobytes()

        words = [
            DummyWord(word="we", start_time_ms=1000, end_time_ms=1300),
            DummyWord(word="think", start_time_ms=1350, end_time_ms=1750),
        ]

        results = aligner.align_words_to_audio(
            words_data=words,
            segment_id="seg-1",
            segment_start_ms=1000,
            segment_end_ms=2000,
            audio_storage_key="test/audio.pcm",
            speaker_label="speaker_001",
            segment_pcm_bytes=synth_pcm,
            sample_rate=sample_rate,
        )

        assert len(results) == 2
        assert results[0].clean_word == "we"
        assert results[0].duration_ms == 300
        assert results[0].alignment_status == "aligned"
        assert results[0].audio_pcm_slice is not None
        # 300ms at 16kHz 16-bit = 0.3 * 16000 * 2 = 9600 bytes
        assert len(results[0].audio_pcm_slice) == 9600

        assert results[1].clean_word == "think"
        assert results[1].duration_ms == 400
        assert len(results[1].audio_pcm_slice) == 12800

    def test_boundary_clamping_for_out_of_bounds_words(self):
        """Clamps timestamps that exceed segment boundaries."""
        aligner = WordAlignmentProcessor()
        sample_rate = 16000
        synth_pcm = (np.ones(sample_rate * 2, dtype=np.int16) * 500).tobytes()

        words = [
            DummyWord(word="project", start_time_ms=900, end_time_ms=2100),  # extends past 1000-2000
        ]

        results = aligner.align_words_to_audio(
            words_data=words,
            segment_id="seg-2",
            segment_start_ms=1000,
            segment_end_ms=2000,
            audio_storage_key="test/audio.pcm",
            speaker_label="speaker_001",
            segment_pcm_bytes=synth_pcm,
            sample_rate=sample_rate,
        )

        assert len(results) == 1
        assert results[0].alignment_status == "boundary_clamped"
        assert results[0].start_time_ms == 1000
        assert results[0].end_time_ms == 2000

    def test_exclude_unrealistically_short_word(self):
        """Word shorter than 60ms is flagged as excluded."""
        aligner = WordAlignmentProcessor()
        words = [
            DummyWord(word="a", start_time_ms=1000, end_time_ms=1030),  # 30ms duration
        ]
        results = aligner.align_words_to_audio(
            words_data=words,
            segment_id="seg-3",
            segment_start_ms=1000,
            segment_end_ms=2000,
            audio_storage_key="test/audio.pcm",
            speaker_label="speaker_001",
        )
        assert results[0].alignment_status == "excluded"
        assert "duration" in (results[0].exclusion_reason or "").lower()
