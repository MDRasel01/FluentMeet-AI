"""
FluentMeet AI - Step 07 Test Suite: ASR Provider
Specification: Step 07 - Section 4 (Speech-to-Text Pipeline)
"""

import pytest
import numpy as np
from unittest.mock import MagicMock
from app.transcription.asr.faster_whisper import FasterWhisperASRProvider
from app.transcription.asr.base import ASRResult, ASRSegment, ASRWord

class TestASRProvider:
    def test_transcribe_empty_bytes_returns_empty_result(self):
        provider = FasterWhisperASRProvider()
        result = provider.transcribe(b"", sample_rate=16000, language="en")
        assert result.text == ""
        assert len(result.segments) == 0
        assert result.confidence is None

    def test_transcribe_with_mock_model(self):
        # Mock WhisperModel output
        mock_word1 = MagicMock()
        mock_word1.word = "Hello"
        mock_word1.start = 0.1
        mock_word1.end = 0.5
        mock_word1.probability = 0.95

        mock_word2 = MagicMock()
        mock_word2.word = "world"
        mock_word2.start = 0.6
        mock_word2.end = 1.0
        mock_word2.probability = 0.98

        mock_seg = MagicMock()
        mock_seg.start = 0.1
        mock_seg.end = 1.0
        mock_seg.text = "Hello world"
        mock_seg.avg_logprob = -0.05
        mock_seg.words = [mock_word1, mock_word2]

        mock_info = MagicMock()
        mock_info.language = "en"

        mock_whisper = MagicMock()
        mock_whisper.transcribe.return_value = ([mock_seg], mock_info)

        provider = FasterWhisperASRProvider(model_instance=mock_whisper)

        # 1.0 second dummy PCM audio
        dummy_pcm = (np.sin(np.linspace(0, 1, 16000)) * 10000).astype(np.int16).tobytes()

        result = provider.transcribe(dummy_pcm, sample_rate=16000)

        assert result.text == "Hello world"
        assert result.language == "en"
        assert len(result.segments) == 1

        seg = result.segments[0]
        assert seg.start_ms == 100
        assert seg.end_ms == 1000
        assert len(seg.words) == 2
        assert seg.words[0].word == "Hello"
        assert seg.words[0].start_ms == 100
        assert seg.words[0].end_ms == 500
        assert seg.words[0].confidence == 0.95
        assert seg.words[1].word == "world"
        assert seg.confidence is not None
        assert 0.90 <= seg.confidence <= 1.0

