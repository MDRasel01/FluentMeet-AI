"""
FluentMeet AI - Step 08 Unit Tests: Preprocessing & Context Detection
"""

import pytest
from app.analysis.preprocessing.cleaner import TranscriptCleaner, CleanedSegment
from app.analysis.preprocessing.context import ContextDetector


class DummySegment:
    def __init__(self, id, text, start_ms=0, end_ms=1000, conf=0.95, speaker_id="spk-1"):
        self.id = id
        self.text = text
        self.start_time_ms = start_ms
        self.end_time_ms = end_ms
        self.duration_ms = end_ms - start_ms
        self.confidence_score = conf
        self.speaker_id = speaker_id


class TestTranscriptCleaner:
    def test_normalize_text_characters(self):
        cleaner = TranscriptCleaner()
        raw = "‘Hello’ “World”—this is…\xa0a test \x00with control chars."
        normalized = cleaner.normalize_text(raw)
        assert "'" in normalized
        assert '"' in normalized
        assert "-" in normalized
        assert "..." in normalized
        assert "\x00" not in normalized
        assert "Hello" in normalized
        assert "World" in normalized

    def test_clean_segment_and_low_confidence(self):
        cleaner = TranscriptCleaner(confidence_threshold=0.70)
        seg1 = DummySegment("seg-1", "High confidence sentence.", conf=0.92)
        seg2 = DummySegment("seg-2", "Low confidence mumble.", conf=0.55)

        c1 = cleaner.clean_segment(seg1, "speaker_001")
        c2 = cleaner.clean_segment(seg2, "speaker_001")

        assert c1.is_low_confidence is False
        assert c2.is_low_confidence is True
        assert c1.word_count == 3
        assert c2.word_count == 3
        assert c1.speaker_label == "speaker_001"

    def test_build_speaker_chunks_with_sliding_overlap(self):
        cleaner = TranscriptCleaner(max_chunk_tokens=15, overlap_segments=1)
        segs = [
            cleaner.clean_segment(DummySegment(f"seg-{i}", f"This is segment number {i} talking about plans.", i * 2000, (i + 1) * 2000), "speaker_user_me")
            for i in range(5)
        ]

        chunks = cleaner.build_speaker_chunks(segs, "speaker_user_me")
        assert len(chunks) > 1
        # Overlap check: segment from chunk 0 must appear as first segment in chunk 1
        assert chunks[1].segments[0].segment_id == chunks[0].segments[-1].segment_id


class TestContextDetector:
    def test_detect_business_context(self):
        detector = ContextDetector()
        text = "Our agenda today covers the quarterly deliverables, timeline milestones, and stakeholder budget alignment."
        ctx = detector.detect_context(text)
        assert ctx.primary_register == "business"
        assert ctx.confidence >= 0.55
        assert "deliverables" in ctx.detected_terms or "agenda" in ctx.detected_terms

    def test_detect_technical_context(self):
        detector = ContextDetector()
        text = "The backend microservice API latency increased after the database query and redis cache deployment."
        ctx = detector.detect_context(text)
        assert ctx.primary_register == "technical"
        assert ctx.confidence >= 0.60
        assert "api" in ctx.detected_terms or "database" in ctx.detected_terms

    def test_detect_interview_context(self):
        detector = ContextDetector()
        text = "Tell me about your previous role, career accomplishments, portfolio background, and greatest strength."
        ctx = detector.detect_context(text)
        assert ctx.primary_register == "interview"
        assert ctx.formality_level == "formal"

    def test_detect_casual_fallback(self):
        detector = ContextDetector()
        text = "We talked about the weekend weather, grabbed a coffee, and chatted about movies."
        ctx = detector.detect_context(text)
        assert ctx.primary_register == "casual"
        assert ctx.formality_level == "casual"
