"""
FluentMeet AI - Step 08 Unit Tests: Fluency Analytics & Timing Metrics
"""

import pytest
from app.analysis.preprocessing.cleaner import CleanedSegment
from app.analysis.modules.fluency import FluencyAnalyzer


def make_timed_segment(seg_id: str, text: str, start: int, end: int) -> CleanedSegment:
    words = len(text.split())
    return CleanedSegment(
        segment_id=seg_id,
        speaker_id="spk-1",
        speaker_label="speaker_001",
        start_time_ms=start,
        end_time_ms=end,
        duration_ms=end - start,
        raw_text=text,
        cleaned_text=text,
        confidence_score=0.98,
        is_low_confidence=False,
        word_count=words,
    )


class TestFluencyAnalyzer:
    def test_fluency_speech_rate_calculation(self):
        analyzer = FluencyAnalyzer()
        # 150 words spoken in 60,000 ms (1.0 minute) -> exactly 150 WPM
        words_chunk = "word " * 150
        segs = [make_timed_segment("seg-1", words_chunk.strip(), 0, 60000)]

        res = analyzer.analyze("speaker_001", segs)
        metrics = {m.metric_name: m.metric_value for m in res["metrics"]}

        assert metrics["speech_rate_wpm"] == 150.0
        assert res["score"] >= 90.0

    def test_fluency_filler_words_detection(self):
        analyzer = FluencyAnalyzer()
        # 6 filler words across 1 minute of speech
        text = "Um I think uh we should basically look at like you know actually this."
        segs = [make_timed_segment("seg-1", text, 0, 60000)]

        res = analyzer.analyze("speaker_001", segs)
        metrics = {m.metric_name: m.metric_value for m in res["metrics"]}

        assert metrics["filler_word_rate"] >= 5.0
        # High filler rate should lower the fluency score
        assert res["score"] < 85.0

    def test_fluency_repetition_rate(self):
        analyzer = FluencyAnalyzer()
        # Immediate repetitions: "we we", "the the"
        text = "we we were thinking that that was fine"
        segs = [make_timed_segment("seg-1", text, 0, 10000)]

        res = analyzer.analyze("speaker_001", segs)
        metrics = {m.metric_name: m.metric_value for m in res["metrics"]}

        assert metrics["repetition_rate"] > 0.0

    def test_empty_segments_fluency(self):
        analyzer = FluencyAnalyzer()
        res = analyzer.analyze("speaker_001", [])
        assert res["status"] == "insufficient_data"
        assert res["metrics"] == []

