"""
FluentMeet AI - Step 08 Unit Tests: Vocabulary Intelligence Module
"""

import pytest
from app.analysis.preprocessing.cleaner import CleanedSegment
from app.analysis.preprocessing.context import MeetingContext
from app.analysis.modules.vocabulary import VocabularyAnalyzer


def make_seg(seg_id: str, text: str) -> CleanedSegment:
    words = len(text.split())
    return CleanedSegment(
        segment_id=seg_id,
        speaker_id="spk-1",
        speaker_label="speaker_001",
        start_time_ms=0,
        end_time_ms=2000,
        duration_ms=2000,
        raw_text=text,
        cleaned_text=text,
        confidence_score=0.95,
        is_low_confidence=False,
        word_count=words,
    )


class TestVocabularyAnalyzer:
    def test_mattr_calculation(self):
        # Repetitive words
        repetitive = ["good", "thing", "good", "thing"] * 25
        mattr_low = VocabularyAnalyzer.calculate_mattr(repetitive, window_size=20)

        # Diverse words
        diverse = [f"word_{i}" for i in range(100)]
        mattr_high = VocabularyAnalyzer.calculate_mattr(diverse, window_size=20)

        assert mattr_high > mattr_low
        assert mattr_high == 1.0

    @pytest.mark.asyncio
    async def test_detect_overused_expressions_and_collocations(self):
        analyzer = VocabularyAnalyzer()
        context = MeetingContext(primary_register="business", confidence=0.85)

        segs = [
            make_seg("seg-1", "We saw good things in the demonstration yesterday."),
            make_seg("seg-2", "We have a very big problem with the database latency."),
            make_seg("seg-3", "We need to make it better before next week."),
            make_seg("seg-4", "There is a lot of things to consider before launch."),
        ]

        result = await analyzer.analyze("speaker_001", segs, context)
        insights = result["insights"]

        assert len(insights) >= 4
        expressions = [i.original_expression.lower() for i in insights]
        assert any("good things" in e for e in expressions)
        assert any("very big problem" in e for e in expressions)
        assert any("make it better" in e for e in expressions)

        for ins in insights:
            assert ins.suggested_expression != ""
            assert ins.example_sentence is not None or ins.explanation != ""

    @pytest.mark.asyncio
    async def test_empty_segments_vocabulary(self):
        analyzer = VocabularyAnalyzer()
        context = MeetingContext(primary_register="business", confidence=0.85)
        res = await analyzer.analyze("speaker_001", [], context)
        assert res["status"] == "insufficient_data"
        assert res["mattr"] == 0.0

