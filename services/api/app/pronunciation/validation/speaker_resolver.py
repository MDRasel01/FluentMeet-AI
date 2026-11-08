"""
FluentMeet AI - Step 09: Speaker Audio Resolver & Source Routing
Specification: Step 09 - Section 5
Manages dual-track audio routing (local_mic vs remote_mix), speaker attribution validation,
and overlapping speech exclusion.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass


@dataclass
class ResolvedSpeakerAudio:
    speaker_id: Optional[str]
    speaker_label: str
    participant_id: Optional[str]
    source_id: int  # 0 = local_mic, 1 = remote_mix
    track_type: str  # local_mic, remote_mix
    audio_segment_ids: List[str]
    total_duration_ms: int
    is_overlapping: bool
    attribution_confidence: float
    is_valid: bool
    exclusion_reason: Optional[str] = None


class SpeakerAudioResolver:
    """
    Resolves audio sources per speaker and prevents cross-talk or double-counting.
    """

    MIN_DIARIZATION_CONFIDENCE = 0.60

    def resolve_speaker_source(
        self,
        speaker_label: str,
        speaker_id: Optional[str],
        participant_id: Optional[str],
        source_id: Optional[int],
        diarization_confidence: Optional[float] = None,
        has_local_mic_audio: bool = True,
    ) -> ResolvedSpeakerAudio:
        """
        Determines the optimal audio track and attribution reliability for a participant.
        """
        # Determine track type
        is_local_user = (
            speaker_label in ("speaker_user_me", "speaker_local", "local_user")
            or source_id == 0
        )

        conf = diarization_confidence if diarization_confidence is not None else 0.90

        if is_local_user:
            # Local user prefers local microphone (source 0)
            target_source = 0 if has_local_mic_audio else 1
            track_type = "local_mic" if target_source == 0 else "remote_mix_fallback"
            attribution_conf = 0.98 if target_source == 0 else 0.85
            is_valid = True
            reason = None
        else:
            # Remote participant uses remote_mix (source 1) with diarization confidence check
            target_source = 1
            track_type = "remote_mix"
            attribution_conf = conf

            if conf < self.MIN_DIARIZATION_CONFIDENCE:
                is_valid = False
                reason = f"LOW_DIARIZATION_CONFIDENCE: Diarization confidence {conf:.2f} is below minimum threshold {self.MIN_DIARIZATION_CONFIDENCE}"
            else:
                is_valid = True
                reason = None

        return ResolvedSpeakerAudio(
            speaker_id=speaker_id,
            speaker_label=speaker_label,
            participant_id=participant_id,
            source_id=target_source,
            track_type=track_type,
            audio_segment_ids=[],
            total_duration_ms=0,
            is_overlapping=False,
            attribution_confidence=round(attribution_conf, 2),
            is_valid=is_valid,
            exclusion_reason=reason,
        )

    @staticmethod
    def identify_overlapping_ranges(
        speech_overlaps: List[Any],
        speaker_label: str,
    ) -> List[Dict[str, int]]:
        """
        Extracts overlapping millisecond ranges where multiple speakers spoke simultaneously.
        """
        overlap_ranges = []
        for ov in speech_overlaps:
            speakers = getattr(ov, "overlapping_speaker_ids", []) or []
            if not speakers or speaker_label in speakers:
                start = getattr(ov, "start_time_ms", 0)
                end = getattr(ov, "end_time_ms", 0)
                if end > start:
                    overlap_ranges.append({"start_ms": start, "end_ms": end})
        return overlap_ranges

    @staticmethod
    def is_word_in_overlap(start_ms: int, end_ms: int, overlaps: List[Dict[str, int]]) -> bool:
        """
        Checks if a word's temporal boundaries fall inside an overlapping speech segment.
        """
        for ov in overlaps:
            # Word overlaps if start is before ov.end and end is after ov.start
            if max(start_ms, ov["start_ms"]) < min(end_ms, ov["end_ms"]):
                return True
        return False
