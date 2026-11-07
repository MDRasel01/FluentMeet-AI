"""
FluentMeet AI - Voice Activity Detection (VAD) Base Provider
Specification: Step 07 - Section 3 (VAD Specification)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SpeechInterval:
    start_ms: int
    end_ms: int
    confidence: float

    @property
    def duration_ms(self) -> int:
        return max(0, self.end_ms - self.start_ms)

class BaseVADProvider(ABC):
    @abstractmethod
    def detect_speech(
        self,
        pcm_bytes: bytes,
        sample_rate: int = 16000,
        threshold: float = 0.5
    ) -> List[SpeechInterval]:
        """
        Detect speech boundaries within 16-bit signed PCM audio.
        Returns list of SpeechInterval with millisecond timestamps and confidence.
        """
        pass
