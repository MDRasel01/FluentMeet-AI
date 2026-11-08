"""
FluentMeet AI - Step 08: Fluency Intelligence Module
Calculates speech rate (WPM), filler word rate, repetition rate, and pause analytics
using Step 07 millisecond timestamps.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.analysis.preprocessing.cleaner import CleanedSegment


@dataclass
class FluencyMetricResult:
    metric_name: str  # speech_rate_wpm, filler_word_rate, repetition_rate, avg_utterance_length_words, pause_frequency
    metric_value: float
    unit: str  # wpm, per_minute, per_100_words, words, count
    evidence_count: int
    confidence: float


FILLER_WORDS = {
    "um", "uh", "erm", "er", "ah", "like", "you know", "actually",
    "basically", "so yeah", "i mean", "sort of", "kind of", "literally"
}


class FluencyAnalyzer:
    """
    Computes mathematical and timing-based fluency metrics from transcript segments.
    """

    def analyze(
        self,
        speaker_label: str,
        segments: List[CleanedSegment],
    ) -> Dict[str, Any]:
        """
        Analyzes fluency metrics based on word timestamps, durations, and text repetitions.
        """
        if not segments:
            return {
                "metrics": [],
                "score": 100.0,
                "status": "insufficient_data",
                "summary": "No segments available for fluency calculation.",
            }

        total_words = sum(s.word_count for s in segments)
        total_duration_ms = sum(s.duration_ms for s in segments)
        duration_minutes = max(0.1, total_duration_ms / 60000.0)

        # 1. Speech Rate (WPM)
        wpm = round(total_words / duration_minutes, 1)

        # 2. Filler word detection
        filler_count = 0
        for seg in segments:
            lower = f" {seg.cleaned_text.lower()} "
            for filler in FILLER_WORDS:
                # Use word boundaries
                matches = len(re.findall(rf"\b{re.escape(filler)}\b", lower))
                filler_count += matches

        filler_rate = round(filler_count / duration_minutes, 2)  # fillers per minute

        # 3. Immediate word repetition (stutter/hesitation) detection: e.g. "we we", "I I", "that that"
        repetition_count = 0
        for seg in segments:
            words = re.findall(r"\b[a-zA-Z]+\b", seg.cleaned_text.lower())
            for i in range(len(words) - 1):
                if words[i] == words[i + 1]:
                    repetition_count += 1

        repetition_rate = round((repetition_count / max(1, total_words)) * 100.0, 2)  # repeats per 100 words

        # 4. Average Utterance Length (words per segment)
        avg_utterance = round(total_words / max(1, len(segments)), 1)

        # 5. Inter-segment pause frequency (silence gaps > 1200ms between this speaker's utterances)
        pause_count = 0
        sorted_segs = sorted(segments, key=lambda s: s.start_time_ms)
        for i in range(len(sorted_segs) - 1):
            gap = sorted_segs[i + 1].start_time_ms - sorted_segs[i].end_time_ms
            if gap >= 1200:
                pause_count += 1

        # Build metric results list
        metrics = [
            FluencyMetricResult(
                metric_name="speech_rate_wpm",
                metric_value=wpm,
                unit="wpm",
                evidence_count=total_words,
                confidence=0.98,
            ),
            FluencyMetricResult(
                metric_name="filler_word_rate",
                metric_value=filler_rate,
                unit="per_minute",
                evidence_count=filler_count,
                confidence=0.95,
            ),
            FluencyMetricResult(
                metric_name="repetition_rate",
                metric_value=repetition_rate,
                unit="per_100_words",
                evidence_count=repetition_count,
                confidence=0.95,
            ),
            FluencyMetricResult(
                metric_name="avg_utterance_length_words",
                metric_value=avg_utterance,
                unit="words",
                evidence_count=len(segments),
                confidence=0.99,
            ),
            FluencyMetricResult(
                metric_name="pause_frequency",
                metric_value=float(pause_count),
                unit="count",
                evidence_count=pause_count,
                confidence=0.92,
            ),
        ]

        # Calculate Fluency Score (0-100)
        # Optimal speech rate: 125 - 165 WPM
        wpm_score = 100.0
        if wpm < 100:
            wpm_score = max(50.0, 100.0 - (100 - wpm) * 0.8)
        elif wpm > 175:
            wpm_score = max(50.0, 100.0 - (wpm - 175) * 0.6)

        # Filler rate scoring: <= 2.0/min is excellent (100), > 6.0/min incurs penalties
        if filler_rate <= 2.0:
            filler_score = 100.0
        else:
            filler_score = max(40.0, 100.0 - (filler_rate - 2.0) * 8.0)

        # Repetition score: < 1.0% is clean
        if repetition_rate <= 1.0:
            rep_score = 100.0
        else:
            rep_score = max(50.0, 100.0 - (repetition_rate - 1.0) * 12.0)

        overall_score = round(0.40 * wpm_score + 0.40 * filler_score + 0.20 * rep_score, 1)

        summary = (
            f"Speaking pace: {wpm} WPM. "
            f"Filler rate: {filler_rate}/min ({filler_count} detected). "
            f"Repetition rate: {repetition_rate}%."
        )

        return {
            "metrics": metrics,
            "score": overall_score,
            "status": "available",
            "evidence_count": len(metrics),
            "summary": summary,
        }
