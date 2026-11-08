"""
FluentMeet AI - Step 09: Prosody Analysis Engine (Pitch, Stress & Intonation)
Specification: Step 09 - Section 10 & Section 11
Extracts fundamental frequency (F0) pitch contours, evaluates syllable prominence / stress,
and scores intonation dynamics.
"""

import math
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class PitchFeatures:
    mean_f0_hz: float
    min_f0_hz: float
    max_f0_hz: float
    pitch_range_hz: float
    contour_type: str  # rising, falling, level, complex
    f0_series: List[float]


@dataclass
class ProsodyReport:
    word_stress_score: float
    sentence_stress_score: float
    intonation_score: float
    pitch_features: PitchFeatures
    syllable_analysis: Dict[str, Any]
    confidence: float


class ProsodyAnalysisEngine:
    """
    Computes acoustic fundamental frequency (F0), intonation contours, and stress patterns.
    """

    def __init__(self, min_f0: float = 75.0, max_f0: float = 400.0):
        self.min_f0 = min_f0
        self.max_f0 = max_f0

    def extract_f0_contour(
        self,
        samples: np.ndarray,
        sample_rate: int = 16000,
        frame_ms: float = 30.0,
        hop_ms: float = 15.0,
    ) -> PitchFeatures:
        """
        Extracts pitch contour across frames using normalized autocorrelation.
        """
        frame_len = int(sample_rate * (frame_ms / 1000.0))
        hop_len = int(sample_rate * (hop_ms / 1000.0))

        min_lag = int(sample_rate / self.max_f0)
        max_lag = int(sample_rate / self.min_f0)

        f0_estimates = []

        if len(samples) < frame_len:
            return PitchFeatures(
                mean_f0_hz=140.0,
                min_f0_hz=140.0,
                max_f0_hz=140.0,
                pitch_range_hz=0.0,
                contour_type="level",
                f0_series=[],
            )

        num_frames = (len(samples) - frame_len) // hop_len + 1
        for i in range(num_frames):
            frame = samples[i * hop_len : i * hop_len + frame_len]
            # Check frame RMS energy
            rms = np.sqrt(np.mean(frame ** 2))
            if rms < 0.02:  # Silence / unvoiced
                continue

            # Autocorrelation
            frame_centered = frame - np.mean(frame)
            autocorr = np.correlate(frame_centered, frame_centered, mode="full")
            autocorr = autocorr[len(frame_centered) - 1 :]

            # Find peak in valid lag range
            if len(autocorr) > max_lag:
                valid_lags = autocorr[min_lag : max_lag + 1]
                peak_lag = min_lag + int(np.argmax(valid_lags))
                peak_val = autocorr[peak_lag]
                norm_peak = peak_val / (autocorr[0] + 1e-9)

                if norm_peak > 0.40:  # Voiced frame
                    f0 = float(sample_rate / peak_lag)
                    f0_estimates.append(f0)

        if not f0_estimates:
            return PitchFeatures(
                mean_f0_hz=135.0,
                min_f0_hz=135.0,
                max_f0_hz=135.0,
                pitch_range_hz=0.0,
                contour_type="level",
                f0_series=[],
            )

        mean_f0 = float(np.mean(f0_estimates))
        min_f0 = float(np.min(f0_estimates))
        max_f0 = float(np.max(f0_estimates))
        pitch_range = float(max_f0 - min_f0)

        # Classify contour
        if len(f0_estimates) >= 4:
            first_half = np.mean(f0_estimates[: len(f0_estimates) // 2])
            second_half = np.mean(f0_estimates[len(f0_estimates) // 2 :])
            diff = second_half - first_half
            if diff > 15.0:
                contour = "rising"
            elif diff < -15.0:
                contour = "falling"
            elif pitch_range > 45.0:
                contour = "complex"
            else:
                contour = "level"
        else:
            contour = "level"

        return PitchFeatures(
            mean_f0_hz=round(mean_f0, 1),
            min_f0_hz=round(min_f0, 1),
            max_f0_hz=round(max_f0, 1),
            pitch_range_hz=round(pitch_range, 1),
            contour_type=contour,
            f0_series=[round(f, 1) for f in f0_estimates[:100]],
        )

    def analyze_prosody(
        self,
        pcm_bytes: Optional[bytes],
        words_count: int,
        sample_rate: int = 16000,
    ) -> ProsodyReport:
        """
        Evaluates intonation dynamics, word stress, and sentence stress.
        """
        if not pcm_bytes or len(pcm_bytes) < 320:
            # Insufficient acoustic buffer
            pf = PitchFeatures(
                mean_f0_hz=130.0,
                min_f0_hz=130.0,
                max_f0_hz=130.0,
                pitch_range_hz=0.0,
                contour_type="level",
                f0_series=[],
            )
            return ProsodyReport(
                word_stress_score=80.0,
                sentence_stress_score=80.0,
                intonation_score=80.0,
                pitch_features=pf,
                syllable_analysis={"estimated_syllables": words_count * 1.4},
                confidence=0.5,
            )

        samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        pitch_feats = self.extract_f0_contour(samples, sample_rate)

        # 1. Intonation Scoring
        # Ideal conversational pitch variation: 35Hz - 120Hz
        p_range = pitch_feats.pitch_range_hz
        if p_range < 15.0:
            # Monotone / robotic intonation
            intonation_score = max(50.0, 70.0 - (15.0 - p_range) * 2.0)
        elif 35.0 <= p_range <= 140.0:
            # Natural dynamic range
            intonation_score = 92.0
        elif p_range > 200.0:
            # Extreme erratic pitch jumps
            intonation_score = max(60.0, 92.0 - (p_range - 200.0) * 0.25)
        else:
            intonation_score = 85.0

        # 2. Syllable and Word Stress
        # Stressed syllables exhibit higher acoustic energy variance
        frame_len = int(sample_rate * 0.05)
        if len(samples) >= frame_len:
            frame_energies = [
                float(np.sqrt(np.mean(samples[i * frame_len : (i + 1) * frame_len] ** 2)))
                for i in range(len(samples) // frame_len)
            ]
            energy_variance = float(np.var(frame_energies))
        else:
            energy_variance = 0.001

        # Healthy rhythm produces distinct peak-to-trough energy contrasts
        if energy_variance > 0.0005:
            word_stress_score = min(100.0, 85.0 + (energy_variance * 5000.0))
            sentence_stress_score = min(100.0, 84.0 + (p_range * 0.12))
        else:
            word_stress_score = 75.0
            sentence_stress_score = 75.0

        estimated_syllables = int(words_count * 1.45)

        return ProsodyReport(
            word_stress_score=round(word_stress_score, 1),
            sentence_stress_score=round(sentence_stress_score, 1),
            intonation_score=round(intonation_score, 1),
            pitch_features=pitch_feats,
            syllable_analysis={
                "estimated_syllables": estimated_syllables,
                "energy_variance": round(energy_variance, 6),
                "rhythm_regularity": "natural" if energy_variance > 0.0005 else "compressed",
            },
            confidence=0.92,
        )

