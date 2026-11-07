"""
FluentMeet AI - Diarization Base Provider & Data Types
Specification: Step 07 - Section 5 (Speaker Diarization Pipeline)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class DiarizationSegment:
    speaker_label: str
    start_ms: int
    end_ms: int
    confidence: Optional[float] = None

    @property
    def duration_ms(self) -> int:
        return max(0, self.end_ms - self.start_ms)

@dataclass
class OverlapInterval:
    start_ms: int
    end_ms: int
    overlapping_speakers: List[str]
    confidence: Optional[float] = None

    @property
    def duration_ms(self) -> int:
        return max(0, self.end_ms - self.start_ms)

@dataclass
class DiarizationResult:
    turns: List[DiarizationSegment] = field(default_factory=list)
    overlaps: List[OverlapInterval] = field(default_factory=list)

class BaseDiarizationProvider(ABC):
    @abstractmethod
    def diarize(
        self,
        pcm_bytes: bytes,
        sample_rate: int = 16000,
        num_speakers: Optional[int] = None,
        source_id: int = 1
    ) -> DiarizationResult:
        """
        Partition PCM audio into speaker turns and detect overlapping speech intervals.
        """
        pass

