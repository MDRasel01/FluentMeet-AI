"""
FluentMeet AI - Step 08: Preprocessing & Transcript Normalization
Handles transcript cleaning, low-confidence tagging, token budgeting, and sliding context windows.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class CleanedSegment:
    segment_id: str
    speaker_id: Optional[str]
    speaker_label: str
    start_time_ms: int
    end_time_ms: int
    duration_ms: int
    raw_text: str
    cleaned_text: str
    confidence_score: Optional[float]
    is_low_confidence: bool
    word_count: int


@dataclass
class ContextChunk:
    chunk_index: int
    speaker_label: str
    segments: List[CleanedSegment] = field(default_factory=list)
    combined_text: str = ""
    estimated_tokens: int = 0
    start_time_ms: int = 0
    end_time_ms: int = 0


class TranscriptCleaner:
    """
    Cleans, normalizes, and structures Step 07 transcript segments for Step 08 AI analysis.
    """

    def __init__(self, confidence_threshold: float = 0.65, max_chunk_tokens: int = 1500, overlap_segments: int = 1):
        self.confidence_threshold = confidence_threshold
        self.max_chunk_tokens = max_chunk_tokens
        self.overlap_segments = overlap_segments

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Cleans and normalizes transcript text:
        - Replaces typographic quotes/dashes with standard ASCII
        - Strips control characters
        - Collapses repeated whitespace
        """
        if not text:
            return ""

        # Normalize unicode quotes and dashes
        replacements = {
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u2013": "-",
            "\u2014": "-",
            "\u2026": "...",
            "\u00a0": " ",
        }
        for k, v in replacements.items():
            text = text.replace(k, v)

        # Remove control characters except newlines/tabs
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        # Collapse excessive whitespace
        text = re.sub(r"[ \t]+", " ", text).strip()
        return text

    def clean_segment(self, segment: Any, speaker_label: str) -> CleanedSegment:
        """
        Converts a DB TranscriptSegment into a structured CleanedSegment.
        """
        raw_text = getattr(segment, "text", "") or ""
        cleaned = self.normalize_text(raw_text)
        conf = getattr(segment, "confidence_score", None)
        is_low = conf is not None and conf < self.confidence_threshold
        words = len(cleaned.split()) if cleaned else 0
        start = getattr(segment, "start_time_ms", 0) or 0
        end = getattr(segment, "end_time_ms", 0) or 0
        duration = getattr(segment, "duration_ms", max(0, end - start))

        return CleanedSegment(
            segment_id=str(getattr(segment, "id", "")),
            speaker_id=str(getattr(segment, "speaker_id", "")) if getattr(segment, "speaker_id", None) else None,
            speaker_label=speaker_label,
            start_time_ms=start,
            end_time_ms=end,
            duration_ms=duration,
            raw_text=raw_text,
            cleaned_text=cleaned,
            confidence_score=conf,
            is_low_confidence=is_low,
            word_count=words,
        )

    def estimate_tokens(self, text: str) -> int:
        """
        Conservative estimate: 1 word ~ 1.33 tokens + 4 tokens overhead.
        """
        words = len(text.split())
        return int(words * 1.33) + 4

    def build_speaker_chunks(self, segments: List[CleanedSegment], speaker_label: str) -> List[ContextChunk]:
        """
        Groups segments belonging to a single speaker into token-budgeted chunks
        with sliding context overlap so AI prompts do not cut thoughts in half.
        """
        speaker_segs = [s for s in segments if s.speaker_label == speaker_label and s.cleaned_text]
        if not speaker_segs:
            return []

        chunks: List[ContextChunk] = []
        current_segs: List[CleanedSegment] = []
        current_tokens = 0
        chunk_idx = 0

        for seg in speaker_segs:
            seg_tokens = self.estimate_tokens(seg.cleaned_text)

            if current_segs and (current_tokens + seg_tokens > self.max_chunk_tokens):
                # Finalize chunk
                chunk = self._create_chunk(chunk_idx, speaker_label, current_segs)
                chunks.append(chunk)
                chunk_idx += 1

                # Sliding overlap: keep the last `overlap_segments`
                overlap = current_segs[-self.overlap_segments :] if self.overlap_segments > 0 else []
                current_segs = list(overlap)
                current_tokens = sum(self.estimate_tokens(s.cleaned_text) for s in current_segs)

            current_segs.append(seg)
            current_tokens += seg_tokens

        if current_segs:
            chunks.append(self._create_chunk(chunk_idx, speaker_label, current_segs))

        return chunks

    def _create_chunk(self, index: int, speaker_label: str, segs: List[CleanedSegment]) -> ContextChunk:
        combined = " ".join(s.cleaned_text for s in segs)
        tokens = self.estimate_tokens(combined)
        start = segs[0].start_time_ms if segs else 0
        end = segs[-1].end_time_ms if segs else 0
        return ContextChunk(
            chunk_index=index,
            speaker_label=speaker_label,
            segments=list(segs),
            combined_text=combined,
            estimated_tokens=tokens,
            start_time_ms=start,
            end_time_ms=end,
        )
