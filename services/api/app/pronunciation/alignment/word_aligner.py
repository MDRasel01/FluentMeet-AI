"""
FluentMeet AI - Step 09: Word-Level Audio Alignment Processor
Specification: Step 09 - Section 7
Validates word timestamps, maps words to audio segments, extracts word acoustic buffers,
and flags timestamp boundary anomalies.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class AlignedWordAudio:
    word: str
    clean_word: str
    start_time_ms: int
    end_time_ms: int
    duration_ms: int
    segment_id: str
    audio_storage_key: Optional[str]
    speaker_label: str
    confidence: float
    alignment_status: str  # aligned, boundary_clamped, unaligned_gap, excluded
    exclusion_reason: Optional[str]
    audio_pcm_slice: Optional[bytes] = None


class WordAlignmentProcessor:
    """
    Validates word-level timestamps and correlates them with exact audio segment buffers.
    """

    MIN_WORD_DURATION_MS = 60  # Minimum realistic spoken English word duration
    MAX_WORD_DURATION_MS = 2500

    def clean_word_token(self, token: str) -> str:
        """
        Strips surrounding punctuation while preserving internal apostrophes (e.g. "don't", "we're").
        """
        if not token:
            return ""
        return token.strip(" .,!?:;\"'()[]{}<>-").lower()

    def align_words_to_audio(
        self,
        words_data: List[Any],
        segment_id: str,
        segment_start_ms: int,
        segment_end_ms: int,
        audio_storage_key: Optional[str],
        speaker_label: str,
        segment_pcm_bytes: Optional[bytes] = None,
        sample_rate: int = 16000,
    ) -> List[AlignedWordAudio]:
        """
        Validates word timestamps, performs boundary clamping, and extracts word acoustic slices.
        """
        aligned_results: List[AlignedWordAudio] = []
        bytes_per_sample = 2  # 16-bit PCM

        prev_end_ms = segment_start_ms

        for w in words_data:
            # Extract word text and timestamps
            raw_text = getattr(w, "word", getattr(w, "text", "")) or ""
            clean_text = self.clean_word_token(raw_text)

            if not clean_text:
                continue

            w_start = getattr(w, "start_time_ms", getattr(w, "start_ms", 0))
            w_end = getattr(w, "end_time_ms", getattr(w, "end_ms", 0))
            w_conf = getattr(w, "confidence_score", getattr(w, "confidence", 0.90))

            duration_ms = max(0, w_end - w_start)
            status = "aligned"
            reason = None

            # Clamp word timestamps to segment boundaries
            clamped = False
            if w_start < segment_start_ms:
                w_start = segment_start_ms
                clamped = True
            if w_end > segment_end_ms:
                w_end = segment_end_ms
                clamped = True
            if clamped:
                duration_ms = max(0, w_end - w_start)

            # 1. Validation checks
            if w_start >= w_end:
                status = "excluded"
                reason = f"Invalid timestamps: start ({w_start}ms) >= end ({w_end}ms)"
            elif duration_ms < self.MIN_WORD_DURATION_MS:
                status = "excluded"
                reason = f"Word duration {duration_ms}ms below minimum threshold {self.MIN_WORD_DURATION_MS}ms"
            elif duration_ms > self.MAX_WORD_DURATION_MS:
                status = "excluded"
                reason = f"Word duration {duration_ms}ms exceeds realistic single word limit"
            elif clamped:
                status = "boundary_clamped"

            # 2. Extract acoustic buffer slice if segment audio buffer is available
            word_pcm_slice = None
            if segment_pcm_bytes and status in ("aligned", "boundary_clamped"):
                rel_start_ms = max(0, w_start - segment_start_ms)
                rel_end_ms = max(rel_start_ms + 10, w_end - segment_start_ms)

                byte_offset_start = int((rel_start_ms / 1000.0) * sample_rate) * bytes_per_sample
                byte_offset_end = int((rel_end_ms / 1000.0) * sample_rate) * bytes_per_sample

                if byte_offset_start < len(segment_pcm_bytes):
                    word_pcm_slice = segment_pcm_bytes[byte_offset_start : min(byte_offset_end, len(segment_pcm_bytes))]

            aligned_results.append(
                AlignedWordAudio(
                    word=raw_text,
                    clean_word=clean_text,
                    start_time_ms=w_start,
                    end_time_ms=w_end,
                    duration_ms=duration_ms,
                    segment_id=segment_id,
                    audio_storage_key=audio_storage_key,
                    speaker_label=speaker_label,
                    confidence=float(w_conf) if w_conf is not None else 0.85,
                    alignment_status=status,
                    exclusion_reason=reason,
                    audio_pcm_slice=word_pcm_slice,
                )
            )
            prev_end_ms = w_end

        return aligned_results
