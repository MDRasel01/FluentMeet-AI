"""
FluentMeet AI - Step 09: Speaking Pace & Pause Analyzer
Specification: Step 09 - Section 12
Analyzes speech tempo (WPM, syllables/min), pause categories (normal, hesitation, boundary),
and tempo consistency.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PauseEvent:
    start_ms: int
    end_ms: int
    duration_ms: int
    pause_type: str  # normal_pause, short_hesitation, long_hesitation, sentence_boundary


@dataclass
class SpeakingPaceReport:
    wpm: float
    syllables_per_minute: float
    active_speaking_ms: int
    total_pause_ms: int
    speech_to_pause_ratio: float
    pace_consistency: str  # steady, variable, rushed, hesitant
    speaking_pace_score: float
    pause_metrics: Dict[str, Any]
    pauses: List[PauseEvent]


class SpeakingPaceAnalyzer:
    """
    Computes WPM, pause taxonomy, and speech-to-pause ratios.
    """

    def analyze_pace(
        self,
        word_timestamps: List[Dict[str, int]],
        total_duration_ms: int,
    ) -> SpeakingPaceReport:
        """
        Analyzes timing boundaries across words to classify pauses and calculate pace score.
        """
        if not word_timestamps:
            return SpeakingPaceReport(
                wpm=0.0,
                syllables_per_minute=0.0,
                active_speaking_ms=0,
                total_pause_ms=total_duration_ms,
                speech_to_pause_ratio=0.0,
                pace_consistency="hesitant",
                speaking_pace_score=50.0,
                pause_metrics={"total_pauses": 0, "avg_pause_ms": 0, "long_pauses_count": 0},
                pauses=[],
            )

        # Sort words by start time
        sorted_words = sorted(word_timestamps, key=lambda w: w.get("start_ms", 0))
        word_count = len(sorted_words)

        pauses: List[PauseEvent] = []
        active_speech_ms = 0
        total_pause_ms = 0

        for i in range(len(sorted_words)):
            w = sorted_words[i]
            w_dur = max(0, w.get("end_ms", 0) - w.get("start_ms", 0))
            active_speech_ms += w_dur

            # Check gap to next word
            if i < len(sorted_words) - 1:
                next_w = sorted_words[i + 1]
                gap_ms = next_w.get("start_ms", 0) - w.get("end_ms", 0)
                if gap_ms >= 150:  # Pause threshold
                    total_pause_ms += gap_ms
                    if gap_ms <= 600:
                        ptype = "normal_pause"
                    elif gap_ms <= 1200:
                        ptype = "short_hesitation"
                    else:
                        ptype = "long_hesitation"

                    pauses.append(
                        PauseEvent(
                            start_ms=w.get("end_ms", 0),
                            end_ms=next_w.get("start_ms", 0),
                            duration_ms=gap_ms,
                            pause_type=ptype,
                        )
                    )

        # Compute conversational speaking duration in minutes (from first word start to last word end)
        elapsed_speech_ms = max(
            1000,
            sorted_words[-1].get("end_ms", 0) - sorted_words[0].get("start_ms", 0),
        )
        speech_minutes = elapsed_speech_ms / 60000.0

        wpm = round(word_count / speech_minutes, 1)
        spm = round(wpm * 1.45, 1)

        # Ratio
        ratio = round(active_speech_ms / max(1, total_pause_ms), 2)

        # Score Speaking Pace (0 - 100)
        # Optimal business English tempo: 125 - 165 WPM
        if 125 <= wpm <= 165:
            pace_score = 95.0
            consistency = "steady"
        elif 100 <= wpm < 125:
            pace_score = 85.0
            consistency = "steady"
        elif 165 < wpm <= 185:
            pace_score = 88.0
            consistency = "rushed"
        elif wpm < 100:
            pace_score = max(50.0, 85.0 - (100 - wpm) * 0.8)
            consistency = "hesitant"
        else:  # > 185
            pace_score = max(50.0, 88.0 - (wpm - 185) * 0.8)
            consistency = "rushed"

        # Long pause deduction
        long_pauses = [p for p in pauses if p.pause_type == "long_hesitation"]
        if len(long_pauses) > 3:
            pace_score = max(50.0, pace_score - len(long_pauses) * 2.5)

        avg_pause = int(total_pause_ms / max(1, len(pauses)))

        return SpeakingPaceReport(
            wpm=wpm,
            syllables_per_minute=spm,
            active_speaking_ms=active_speech_ms,
            total_pause_ms=total_pause_ms,
            speech_to_pause_ratio=ratio,
            pace_consistency=consistency,
            speaking_pace_score=round(pace_score, 1),
            pause_metrics={
                "total_pauses": len(pauses),
                "avg_pause_ms": avg_pause,
                "long_pauses_count": len(long_pauses),
            },
            pauses=pauses,
        )
