"""
FluentMeet AI - Step 06 Test Suite: Stream Synchronization & Gap Detection
Specification: Step 06 - Section 10, 11 & 21 (REQ-ING-008, REQ-ING-009)
"""

import pytest
from app.audio.streams.sequence_manager import SequenceManager
from app.audio.streams.synchronizer import AudioSynchronizer

class TestSequenceManager:
    def test_monotonic_sequences(self):
        sm = SequenceManager()
        # Source 0
        r1 = sm.check_sequence(source_id=0, sequence_number=1)
        assert r1.is_valid is True
        assert r1.is_duplicate is False
        assert r1.gap_range is None

        r2 = sm.check_sequence(source_id=0, sequence_number=2)
        assert r2.is_valid is True
        assert r2.is_duplicate is False
        assert r2.gap_range is None

    def test_duplicate_rejection(self):
        sm = SequenceManager()
        sm.check_sequence(source_id=0, sequence_number=1)
        sm.check_sequence(source_id=0, sequence_number=2)

        # Duplicate seq 2
        dup = sm.check_sequence(source_id=0, sequence_number=2)
        assert dup.is_duplicate is True
        assert dup.is_valid is False

        # Out-of-order older seq 1
        old = sm.check_sequence(source_id=0, sequence_number=1)
        assert old.is_duplicate is True
        assert old.is_valid is False

    def test_gap_detection(self):
        sm = SequenceManager()
        sm.check_sequence(source_id=0, sequence_number=1)
        # Jump from 1 to 5
        r_jump = sm.check_sequence(source_id=0, sequence_number=5)
        assert r_jump.is_valid is True
        assert r_jump.gap_range == (2, 4)

    def test_independent_sources(self):
        sm = SequenceManager()
        # Source 0 and Source 1 track sequences completely independently
        sm.check_sequence(source_id=0, sequence_number=10)
        sm.check_sequence(source_id=1, sequence_number=1)

        r_source0_next = sm.check_sequence(source_id=0, sequence_number=11)
        assert r_source0_next.is_valid is True
        assert r_source0_next.gap_range is None

        r_source1_next = sm.check_sequence(source_id=1, sequence_number=2)
        assert r_source1_next.is_valid is True
        assert r_source1_next.gap_range is None

class TestAudioSynchronizer:
    def test_clock_drift_tracking(self):
        sync = AudioSynchronizer()
        # 1600 samples at 16kHz = exactly 100ms
        diag1 = sync.track_chunk(source_id=0, session_timestamp_ms=0.0, sample_count=1600)
        assert diag1.clock_drift_ms == 0.0

        # Chunk 2 arrives at 105ms (5ms drift)
        diag2 = sync.track_chunk(source_id=0, session_timestamp_ms=105.0, sample_count=1600)
        assert abs(diag2.clock_drift_ms - 5.0) < 0.1
        assert diag2.is_drift_warning is False

        # Large drift (e.g. 600ms network delay)
        diag3 = sync.track_chunk(source_id=0, session_timestamp_ms=800.0, sample_count=1600)
        assert diag3.is_drift_warning is True
