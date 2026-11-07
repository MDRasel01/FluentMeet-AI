"""
FluentMeet AI - Step 07 Test Suite: Voice Activity Detection (VAD)
Specification: Step 07 - Section 3 (VAD Quality Gate)
"""

import pytest
import numpy as np
from app.transcription.vad.silero import SileroVADProvider
from app.transcription.vad.base import SpeechInterval

def generate_tone(freq: float, duration_s: float, sample_rate: int = 16000, amplitude: int = 15000) -> bytes:
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    samples = (np.sin(2 * np.pi * freq * t) * amplitude).astype(np.int16)
    return samples.tobytes()

def generate_silence(duration_s: float, sample_rate: int = 16000) -> bytes:
    return np.zeros(int(sample_rate * duration_s), dtype=np.int16).tobytes()

class TestVoiceActivityDetection:
    def test_silence_returns_empty_intervals(self):
        vad = SileroVADProvider(min_speech_duration_ms=250)
        silence_pcm = generate_silence(duration_s=2.0)
        intervals = vad.detect_speech(silence_pcm, sample_rate=16000)
        assert len(intervals) == 0

    def test_empty_pcm_returns_empty_intervals(self):
        vad = SileroVADProvider()
        assert vad.detect_speech(b"", sample_rate=16000) == []

    def test_clean_speech_tone_detected(self):
        vad = SileroVADProvider(min_speech_duration_ms=250)
        # 1.5 seconds of clean active speech tone
        speech_pcm = generate_tone(freq=300.0, duration_s=1.5, amplitude=14000)
        intervals = vad.detect_speech(speech_pcm, sample_rate=16000)

        assert len(intervals) >= 1
        first_interval = intervals[0]
        assert first_interval.duration_ms >= 250
        assert first_interval.confidence > 0.5

    def test_speech_surrounded_by_silence(self):
        vad = SileroVADProvider(min_speech_duration_ms=250, min_silence_duration_ms=100)
        # 0.5s silence + 1.0s speech + 0.5s silence
        silence_pre = generate_silence(0.5)
        speech = generate_tone(freq=400.0, duration_s=1.0, amplitude=15000)
        silence_post = generate_silence(0.5)
        audio = silence_pre + speech + silence_post

        intervals = vad.detect_speech(audio, sample_rate=16000)
        assert len(intervals) >= 1
        # Speech segment should start roughly after 400ms and end before 1600ms
        assert intervals[0].start_ms >= 300
        assert intervals[0].end_ms <= 1650

