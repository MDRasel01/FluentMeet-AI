"""
FluentMeet AI - Speaker-Transcript Word Alignment Engine
Specification: Step 07 - Section 6 (Alignment & Reconciled Timeline)
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import numpy as np

from app.transcription.asr.base import ASRWord, ASRSegment, ASRResult
from app.transcription.diarization.base import DiarizationSegment, DiarizationResult, OverlapInterval

logger = logging.getLogger("transcription.alignment")

@dataclass
class AlignedWord:
    word: str
    start_ms: int
    end_ms: int
    speaker_label: str
    confidence: Optional[float] = None
    is_overlapping: bool = False

@dataclass
class AlignedSegment:
    speaker_label: str
    start_time_ms: int
    end_time_ms: int
    text: str
    confidence_score: Optional[float]
    words: List[AlignedWord] = field(default_factory=list)
    status: str = "final"

    @property
    def duration_ms(self) -> int:
        return max(0, self.end_time_ms - self.start_time_ms)

@dataclass
class AlignmentOutput:
    segments: List[AlignedSegment] = field(default_factory=list)
    overlaps: List[OverlapInterval] = field(default_factory=list)
    word_count: int = 0

class SpeakerTranscriptAligner:
    """
    Precision temporal aligner mapping Whisper word timestamps to Pyannote speaker turns.
    Resolves boundaries using maximum temporal intersection.
    """

    @classmethod
    def align(
        cls,
        asr_result: ASRResult,
        diarization_result: DiarizationResult,
        default_speaker_label: str = "speaker_001"
    ) -> AlignmentOutput:
        # Collect all words across all ASR segments
        all_words: List[ASRWord] = []
        for seg in asr_result.segments:
            if seg.words:
                all_words.extend(seg.words)
            else:
                # If no word-level timestamps were provided, treat segment as a single word/utterance
                all_words.append(ASRWord(
                    word=seg.text,
                    start_ms=seg.start_ms,
                    end_ms=seg.end_ms,
                    confidence=seg.confidence
                ))

        if not all_words:
            # Fallback if text exists but no segments
            if asr_result.text.strip():
                return AlignmentOutput(
                    segments=[
                        AlignedSegment(
                            speaker_label=default_speaker_label,
                            start_time_ms=0,
                            end_time_ms=0,
                            text=asr_result.text.strip(),
                            confidence_score=asr_result.confidence,
                            words=[]
                        )
                    ],
                    overlaps=diarization_result.overlaps,
                    word_count=len(asr_result.text.split())
                )
            return AlignmentOutput(segments=[], overlaps=diarization_result.overlaps, word_count=0)

        turns = diarization_result.turns
        overlaps = diarization_result.overlaps

        aligned_words: List[AlignedWord] = []

        for word in all_words:
            assigned_speaker = default_speaker_label
            max_overlap = -1
            best_turn: Optional[DiarizationSegment] = None

            # Calculate temporal overlap with each speaker turn
            for turn in turns:
                overlap_start = max(word.start_ms, turn.start_ms)
                overlap_end = min(word.end_ms, turn.end_ms)
                overlap_duration = max(0, overlap_end - overlap_start)

                if overlap_duration > max_overlap:
                    max_overlap = overlap_duration
                    best_turn = turn

            if best_turn is not None and max_overlap > 0:
                assigned_speaker = best_turn.speaker_label
            elif turns:
                # If no direct overlap (e.g. drift), assign to temporally nearest turn
                nearest_turn = min(
                    turns,
                    key=lambda t: min(abs(word.start_ms - t.end_ms), abs(word.end_ms - t.start_ms))
                )
                assigned_speaker = nearest_turn.speaker_label

            # Check if this word falls within an overlap interval
            is_in_overlap = any(
                max(word.start_ms, o.start_ms) < min(word.end_ms, o.end_ms)
                for o in overlaps
            )

            aligned_words.append(AlignedWord(
                word=word.word,
                start_ms=word.start_ms,
                end_ms=word.end_ms,
                speaker_label=assigned_speaker,
                confidence=word.confidence,
                is_overlapping=is_in_overlap
            ))

        # Group contiguous words by speaker into AlignedSegments
        segments: List[AlignedSegment] = []
        if not aligned_words:
            return AlignmentOutput(segments=[], overlaps=overlaps, word_count=0)

        current_words: List[AlignedWord] = []
        current_speaker: Optional[str] = None

        for w in aligned_words:
            if current_speaker is None:
                current_speaker = w.speaker_label
                current_words = [w]
            elif w.speaker_label == current_speaker:
                current_words.append(w)
            else:
                # Flush previous segment
                segments.append(cls._build_segment(current_speaker, current_words))
                current_speaker = w.speaker_label
                current_words = [w]

        if current_words and current_speaker is not None:
            segments.append(cls._build_segment(current_speaker, current_words))

        return AlignmentOutput(
            segments=segments,
            overlaps=overlaps,
            word_count=len(aligned_words)
        )

    @staticmethod
    def _build_segment(speaker_label: str, words: List[AlignedWord]) -> AlignedSegment:
        text = " ".join(w.word for w in words).strip()
        start_ms = words[0].start_ms
        end_ms = words[-1].end_ms
        confs = [w.confidence for w in words if w.confidence is not None]
        avg_conf = round(float(np.mean(confs)), 4) if confs else None

        return AlignedSegment(
            speaker_label=speaker_label,
            start_time_ms=start_ms,
            end_time_ms=end_ms,
            text=text,
            confidence_score=avg_conf,
            words=words,
            status="final"
        )

