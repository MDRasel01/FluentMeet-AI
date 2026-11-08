"""
FluentMeet AI - Step 08 Unit Tests: Grammar Intelligence Module
"""

import pytest
from app.analysis.preprocessing.cleaner import CleanedSegment
from app.analysis.preprocessing.context import MeetingContext
from app.analysis.modules.grammar import GrammarAnalyzer


def make_cleaned_segment(seg_id: str, text: str, start: int = 0, end: int = 2000, speaker: str = "speaker_001") -> CleanedSegment:
    words = len(text.split())
    return CleanedSegment(
        segment_id=seg_id,
        speaker_id="spk-1",
        speaker_label=speaker,
        start_time_ms=start,
        end_time_ms=end,
        duration_ms=end - start,
        raw_text=text,
        cleaned_text=text,
        confidence_score=0.95,
        is_low_confidence=False,
        word_count=words,
    )


class TestGrammarAnalyzer:
    @pytest.mark.asyncio
    async def test_detect_deterministic_esl_patterns(self):
        analyzer = GrammarAnalyzer()
        context = MeetingContext(primary_register="business", confidence=0.8)

        segs = [
            make_cleaned_segment("seg-1", "He don't know the exact schedule."),
            make_cleaned_segment("seg-2", "We was discussing the project budget."),
            make_cleaned_segment("seg-3", "Let's discuss about the proposal."),
            make_cleaned_segment("seg-4", "It will depend of the client approval."),
            make_cleaned_segment("seg-5", "They didn't went to the meeting."),
            make_cleaned_segment("seg-6", "We don't have no extra resources for this sprint."),
        ]

        result = await analyzer.analyze("speaker_001", segs, context)
        issues = result["issues"]

        assert len(issues) >= 6
        categories = {i.category for i in issues}
        assert "subject_verb_agreement" in categories
        assert "prepositions" in categories
        assert "tense" in categories

        # Verified segment linkage
        for issue in issues:
            assert issue.segment_id in {"seg-1", "seg-2", "seg-3", "seg-4", "seg-5", "seg-6"}
            assert issue.confidence >= 0.90
            assert issue.evidence_status == "verified"

    @pytest.mark.asyncio
    async def test_grammar_scoring_with_deductions(self):
        analyzer = GrammarAnalyzer()
        context = MeetingContext(primary_register="business", confidence=0.8)

        clean_segs = [
            make_cleaned_segment("seg-c1", "We have completed the deployment on time and all unit tests passed successfully."),
            make_cleaned_segment("seg-c2", "The client agreed with our proposed timeline and signed the contract yesterday."),
        ]
        clean_result = await analyzer.analyze("speaker_001", clean_segs, context)
        assert clean_result["score"] >= 85.0

        error_segs = [
            make_cleaned_segment("seg-e1", "We was planning to discuss about the budget."),
            make_cleaned_segment("seg-e2", "He don't have no time for this project."),
        ]
        error_result = await analyzer.analyze("speaker_001", error_segs, context)
        assert error_result["score"] < clean_result["score"]

    @pytest.mark.asyncio
    async def test_empty_segments_insufficient_data(self):
        analyzer = GrammarAnalyzer()
        context = MeetingContext(primary_register="business", confidence=0.8)
        result = await analyzer.analyze("speaker_001", [], context)
        assert result["status"] == "insufficient_data"
        assert result["issues"] == []

