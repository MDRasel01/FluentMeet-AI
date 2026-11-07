"""
FluentMeet AI - Step 07 Test Suite: Speaker-Transcript Alignment
Specification: Step 07 - Section 6 (Alignment & Reconciled Timeline)
"""

import pytest
from app.transcription.asr.base import ASRResult, ASRSegment, ASRWord
from app.transcription.diarization.base import DiarizationResult, DiarizationSegment, OverlapInterval
from app.transcription.alignment.aligner import SpeakerTranscriptAligner

class TestSpeakerTranscriptAligner:
    def test_align_single_speaker(self):
        words = [
            ASRWord(word="Good", start_ms=100, end_ms=300, confidence=0.95),
            ASRWord(word="morning", start_ms=350, end_ms=650, confidence=0.98),
            ASRWord(word="everyone", start_ms=700, end_ms=1200, confidence=0.92),
        ]
        seg = ASRSegment(start_ms=100, end_ms=1200, text="Good morning everyone", words=words)
        asr_res = ASRResult(text="Good morning everyone", language="en", segments=[seg])

        turns = [
            DiarizationSegment(speaker_label="speaker_user_me", start_ms=0, end_ms=1500, confidence=0.99)
        ]
        diar_res = DiarizationResult(turns=turns, overlaps=[])

        alignment = SpeakerTranscriptAligner.align(asr_res, diar_res)
        assert len(alignment.segments) == 1
        out_seg = alignment.segments[0]
        assert out_seg.speaker_label == "speaker_user_me"
        assert out_seg.text == "Good morning everyone"
        assert len(out_seg.words) == 3
        assert out_seg.start_time_ms == 100
        assert out_seg.end_time_ms == 1200

    def test_align_multi_speaker_turn_split(self):
        # Words spanning across two speaker turns
        words = [
            ASRWord(word="I", start_ms=200, end_ms=400, confidence=0.9),
            ASRWord(word="agree", start_ms=450, end_ms=800, confidence=0.95),
            ASRWord(word="Thank", start_ms=1100, end_ms=1400, confidence=0.92),
            ASRWord(word="you", start_ms=1450, end_ms=1700, confidence=0.96),
        ]
        seg = ASRSegment(start_ms=200, end_ms=1700, text="I agree Thank you", words=words)
        asr_res = ASRResult(text="I agree Thank you", language="en", segments=[seg])

        turns = [
            DiarizationSegment(speaker_label="speaker_001", start_ms=100, end_ms=900, confidence=0.9),
            DiarizationSegment(speaker_label="speaker_002", start_ms=1000, end_ms=2000, confidence=0.9),
        ]
        diar_res = DiarizationResult(turns=turns, overlaps=[])

        alignment = SpeakerTranscriptAligner.align(asr_res, diar_res)
        assert len(alignment.segments) == 2

        # First segment should be speaker_001
        assert alignment.segments[0].speaker_label == "speaker_001"
        assert alignment.segments[0].text == "I agree"

        # Second segment should be speaker_002
        assert alignment.segments[1].speaker_label == "speaker_002"
        assert alignment.segments[1].text == "Thank you"

    def test_word_in_overlap_zone_flagged(self):
        words = [
            ASRWord(word="Wait", start_ms=1000, end_ms=1300, confidence=0.8),
        ]
        seg = ASRSegment(start_ms=1000, end_ms=1300, text="Wait", words=words)
        asr_res = ASRResult(text="Wait", language="en", segments=[seg])

        turns = [
            DiarizationSegment("speaker_001", 900, 1500, 0.9),
            DiarizationSegment("speaker_002", 950, 1400, 0.85),
        ]
        overlaps = [
            OverlapInterval(950, 1400, ["speaker_001", "speaker_002"], 0.88)
        ]
        diar_res = DiarizationResult(turns=turns, overlaps=overlaps)

        alignment = SpeakerTranscriptAligner.align(asr_res, diar_res)
        assert len(alignment.segments) == 1
        assert alignment.segments[0].words[0].is_overlapping is True
