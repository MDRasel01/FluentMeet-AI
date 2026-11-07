"""
FluentMeet AI - ASR Base Provider & Data Types
Specification: Step 07 - Section 4 (Speech-to-Text Pipeline)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ASRWord:
    word: str
    start_ms: int
    end_ms: int
    confidence: Optional[float] = None

@dataclass
class ASRSegment:
    start_ms: int
    end_ms: int
    text: str
    confidence: Optional[float] = None
    words: List[ASRWord] = field(default_factory=list)

    @property
    def duration_ms(self) -> int:
        return max(0, self.end_ms - self.start_ms)

@dataclass
class ASRResult:
    text: str
    language: str
    segments: List[ASRSegment] = field(default_factory=list)
    confidence: Optional[float] = None

class BaseASRProvider(ABC):
    @abstractmethod
    def transcribe(
        self,
        pcm_bytes: bytes,
        sample_rate: int = 16000,
        language: str = "en"
    ) -> ASRResult:
        """
        Transcribe 16-bit PCM audio returning structured segments and word timestamps.
        """
        pass
