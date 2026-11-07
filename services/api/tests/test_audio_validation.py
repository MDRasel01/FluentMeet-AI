"""
FluentMeet AI - Step 06 Test Suite: Audio Validation & Metrics
Specification: Step 06 - Section 8, 9 & 21 (REQ-ING-006, REQ-ING-007)
"""

import pytest
import numpy as np
from app.audio.validator import AudioValidator, AudioValidationError, QualityClassification

class TestAudioValidator:
    def test_validate_format_success(self):
        # 160 samples = 320 bytes PCM S16LE
        pcm = np.zeros(160, dtype=np.int16).tobytes()
        AudioValidator.validate_format(
            sample_rate=16000,
            channels=1,
            sample_count=160,
            pcm_bytes=pcm
        )

    def test_validate_format_invalid_sample_rate(self):
        pcm = np.zeros(160, dtype=np.int16).tobytes()
        with pytest.raises(AudioValidationError) as exc:
            AudioValidator.validate_format(
                sample_rate=48000,
                channels=1,
                sample_count=160,
                pcm_bytes=pcm
            )
        assert "Invalid sample rate" in str(exc.value)

    def test_validate_format_invalid_channels(self):
        pcm = np.zeros(160, dtype=np.int16).tobytes()
        with pytest.raises(AudioValidationError) as exc:
            AudioValidator.validate_format(
                sample_rate=16000,
                channels=2,
                sample_count=160,
                pcm_bytes=pcm
            )
        assert "Invalid channel count" in str(exc.value)

    def test_calculate_metrics_silence(self):
        # 1000 zero samples = silence
        silence = np.zeros(1000, dtype=np.int16).tobytes()
        metrics = AudioValidator.calculate_metrics(silence, sample_rate=16000)
        assert metrics.rms_level == 0.0
        assert metrics.peak_amplitude == 0.0
        assert metrics.silence_ratio == 1.0
        assert metrics.clipping_ratio == 0.0

    def test_calculate_metrics_clipping_detection(self):
        # Samples hitting full scale 32767
        clipped = np.full(1000, 32767, dtype=np.int16).tobytes()
        metrics = AudioValidator.calculate_metrics(clipped, sample_rate=16000)
        assert metrics.clipping_ratio == 1.0
        assert metrics.peak_amplitude == 1.0

    def test_calculate_metrics_normal_sine_wave(self):
        # 440 Hz tone at 50% max amplitude
        t = np.linspace(0, 0.1, 1600, endpoint=False)
        waveform = (np.sin(2 * np.pi * 440 * t) * 16384).astype(np.int16)
        metrics = AudioValidator.calculate_metrics(waveform.tobytes(), sample_rate=16000)

        assert 0.3 < metrics.rms_level < 0.4
        assert abs(metrics.peak_amplitude - 0.5) < 0.05
        assert metrics.clipping_ratio == 0.0
        assert metrics.silence_ratio < 0.2

    def test_classify_quality(self):
        # Valid metrics
        t = np.linspace(0, 0.1, 1600, endpoint=False)
        normal = (np.sin(2 * np.pi * 440 * t) * 16384).astype(np.int16)
        metrics = AudioValidator.calculate_metrics(normal.tobytes(), 16000)
        status = AudioValidator.classify_quality(metrics)
        assert status in [QualityClassification.VALID, QualityClassification.VALID_WITH_WARNINGS]

        # Heavy clipping metrics
        clipped = np.full(1600, 32767, dtype=np.int16).tobytes()
        metrics_clipped = AudioValidator.calculate_metrics(clipped, 16000)
        status_clipped = AudioValidator.classify_quality(metrics_clipped)
        assert status_clipped == QualityClassification.DEGRADED
