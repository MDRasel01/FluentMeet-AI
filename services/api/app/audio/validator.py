"""
FluentMeet AI - Audio Validation & Quality Metrics Engine
Specification: Step 06 - Section 8 & Section 17
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple

class QualityClassification:
    VALID = "VALID"
    VALID_WITH_WARNINGS = "VALID_WITH_WARNINGS"
    DEGRADED = "DEGRADED"
    INVALID = "INVALID"

@dataclass
class QualityMetrics:
    rms_level: float
    peak_amplitude: float
    clipping_ratio: float
    silence_ratio: float
    invalid_sample_count: int
    duration_ms: int
    quality_status: str  # VALID, VALID_WITH_WARNINGS, DEGRADED, INVALID

class AudioValidationError(Exception):
    """Raised when audio format or integrity validation fails."""
    pass

class AudioValidator:
    SUPPORTED_SAMPLE_RATES = {16000}
    TARGET_SAMPLE_RATE = 16000
    TARGET_CHANNELS = 1

    @classmethod
    def validate_format(cls, sample_rate: int, channels: int, sample_count: int, pcm_bytes: bytes) -> None:
        if sample_rate not in cls.SUPPORTED_SAMPLE_RATES:
            raise AudioValidationError(f"Invalid sample rate: {sample_rate} Hz. Expected {cls.TARGET_SAMPLE_RATE} Hz")

        if channels != cls.TARGET_CHANNELS:
            raise AudioValidationError(f"Invalid channel count: {channels}. Expected {cls.TARGET_CHANNELS} (mono)")

        if len(pcm_bytes) % 2 != 0:
            raise AudioValidationError(f"PCM byte length must be even: got {len(pcm_bytes)} bytes")

        actual_samples = len(pcm_bytes) // 2
        if actual_samples != sample_count:
            raise AudioValidationError(
                f"Sample count mismatch: metadata specifies {sample_count}, but payload contains {actual_samples}"
            )

    @staticmethod
    def calculate_metrics(pcm_bytes: bytes, sample_rate: int = 16000) -> QualityMetrics:
        if not pcm_bytes:
            return QualityMetrics(
                rms_level=0.0,
                peak_amplitude=0.0,
                clipping_ratio=0.0,
                silence_ratio=1.0,
                invalid_sample_count=0,
                duration_ms=0,
                quality_status=QualityClassification.INVALID
            )

        # Convert bytes to numpy 16-bit signed integers
        samples = np.frombuffer(pcm_bytes, dtype=np.int16)
        total_samples = len(samples)

        if total_samples == 0:
            return QualityMetrics(
                rms_level=0.0,
                peak_amplitude=0.0,
                clipping_ratio=0.0,
                silence_ratio=1.0,
                invalid_sample_count=0,
                duration_ms=0,
                quality_status=QualityClassification.INVALID
            )

        # Normalization to [-1.0, 1.0]
        float_samples = samples.astype(np.float32) / 32768.0

        # 1. RMS level
        rms = float(np.sqrt(np.mean(float_samples ** 2)))

        # 2. Peak amplitude
        peak = float(np.max(np.abs(float_samples)))

        # 3. Clipping ratio (samples within 2 counts of max 32767 or min -32768)
        clipped_samples = np.sum(np.abs(samples) >= 32765)
        clipping_ratio = float(clipped_samples / total_samples)

        # 4. Silence ratio (samples with abs amplitude < 0.005)
        silent_samples = np.sum(np.abs(float_samples) < 0.005)
        silence_ratio = float(silent_samples / total_samples)

        # Duration
        duration_ms = int((total_samples / sample_rate) * 1000)

        # Overall classification
        if clipping_ratio > 0.05 or (rms < 0.001 and silence_ratio > 0.99 and duration_ms > 2000):
            status = QualityClassification.DEGRADED
        elif clipping_ratio > 0.01 or rms < 0.01:
            status = QualityClassification.VALID_WITH_WARNINGS
        else:
            status = QualityClassification.VALID

        return QualityMetrics(
            rms_level=round(rms, 4),
            peak_amplitude=round(peak, 4),
            clipping_ratio=round(clipping_ratio, 4),
            silence_ratio=round(silence_ratio, 4),
            invalid_sample_count=0,
            duration_ms=duration_ms,
            quality_status=status
        )

    @staticmethod
    def classify_quality(metrics: QualityMetrics) -> str:
        return metrics.quality_status
