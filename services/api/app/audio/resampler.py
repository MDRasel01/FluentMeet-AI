"""
FluentMeet AI - Audio Normalization & Resampling Engine
Specification: Step 06 - Section 9
"""

import math
import numpy as np
from scipy import signal

class AudioNormalizer:
    TARGET_SAMPLE_RATE = 16000

    @classmethod
    def normalize_pcm(cls, pcm_bytes: bytes, input_sample_rate: int) -> bytes:
        """
        Ensures PCM S16LE audio is normalized to 16,000 Hz Mono.
        Bypasses transformation if already at target sample rate.
        """
        if input_sample_rate == cls.TARGET_SAMPLE_RATE:
            return pcm_bytes

        # Load input Int16 samples
        samples = np.frombuffer(pcm_bytes, dtype=np.int16)
        if len(samples) == 0:
            return pcm_bytes

        # Calculate GCD for polyphase resampling
        gcd = math.gcd(cls.TARGET_SAMPLE_RATE, input_sample_rate)
        up = cls.TARGET_SAMPLE_RATE // gcd
        down = input_sample_rate // gcd

        # Perform high-quality polyphase filtering resample
        float_samples = samples.astype(np.float32)
        resampled_float = signal.resample_poly(float_samples, up, down)

        # Clamp and convert back to Int16
        clamped = np.clip(resampled_float, -32768, 32767).astype(np.int16)
        return clamped.tobytes()
