"""
FluentMeet AI - Step 09 Test Suite: Audio Evidence Validation & Routing
Specification: Step 09 - Section 4, 5, 6
"""

import pytest
import numpy as np
from unittest.mock import MagicMock
from app.pronunciation.validation.evidence_validator import AudioEvidenceValidator, AudioQualityReport
from app.pronunciation.validation.speaker_resolver import SpeakerAudioResolver, ResolvedSpeakerAudio


class TestAudioEvidenceValidation:
    def test_audio_quality_suitable_speech(self):
        """Clean synthetic speech tone with positive SNR and no clipping."""
        validator = AudioEvidenceValidator()
        sample_rate = 16000
        t = np.linspace(0, 1.0, sample_rate, False)
        # 220Hz tone + mild noise
        sine_wave = 0.5 * np.sin(2 * np.pi * 220 * t)
        noise = 0.01 * np.random.normal(0, 1, sample_rate)
        pcm_floats = sine_wave + noise
        pcm_bytes = (pcm_floats * 32767).astype(np.int16).tobytes()

        report: AudioQualityReport = validator.analyze_audio_quality(pcm_bytes, sample_rate=sample_rate)

        assert report.is_suitable is True
        assert report.status == "suitable"
        assert report.snr_db > 10.0
        assert report.clipping_ratio < 0.01
        assert report.duration_ms == 1000

    def test_audio_quality_severe_clipping(self):
        """Audio with heavy clipping should be flagged as low_quality."""
        validator = AudioEvidenceValidator()
        sample_rate = 16000
        # Extreme amplitude causing 50% clipping
        clipped = np.full(sample_rate, 32767, dtype=np.int16)
        pcm_bytes = clipped.tobytes()

        report: AudioQualityReport = validator.analyze_audio_quality(pcm_bytes, sample_rate=sample_rate)

        assert report.is_suitable is False
        assert report.status == "low_quality"
        assert report.clipping_ratio > 0.05
        assert "clipping" in (report.exclusion_reason or "").lower()

    def test_audio_quality_excessive_silence(self):
        """Audio that is almost completely silent should be flagged as insufficient_speech."""
        validator = AudioEvidenceValidator()
        sample_rate = 16000
        silent = np.zeros(sample_rate * 2, dtype=np.int16)
        pcm_bytes = silent.tobytes()

        report: AudioQualityReport = validator.analyze_audio_quality(pcm_bytes, sample_rate=sample_rate)

        assert report.is_suitable is False
        assert report.status == "insufficient_speech"
        assert report.silence_ratio > 0.80

    def test_audio_quality_empty_buffer(self):
        """Empty or corrupt PCM buffer returns processing_failed."""
        validator = AudioEvidenceValidator()
        report = validator.analyze_audio_quality(b"")
        assert report.is_suitable is False
        assert report.status == "processing_failed"

    def test_storage_reference_validation(self):
        """Validates object storage reference presence and error handling."""
        mock_storage = MagicMock()
        mock_storage.get_object.return_value = b"\x00\x00" * 800

        validator = AudioEvidenceValidator(storage_service=mock_storage)

        # Valid reference
        is_valid, err, audio_bytes = validator.validate_audio_reference("valid/path.pcm")
        assert is_valid is True
        assert err is None
        assert audio_bytes is not None

        # Missing reference key
        is_valid, err, _ = validator.validate_audio_reference(None)
        assert is_valid is False
        assert err == "AUDIO_NOT_FOUND"

        # Not found in storage
        mock_storage.get_object.side_effect = FileNotFoundError()
        is_valid, err, _ = validator.validate_audio_reference("missing/key.pcm")
        assert is_valid is False
        assert err == "AUDIO_NOT_FOUND"


class TestSpeakerAudioResolver:
    def test_resolve_local_user_mic(self):
        """Local speaker prioritizes local_mic (source 0)."""
        resolver = SpeakerAudioResolver()
        resolved: ResolvedSpeakerAudio = resolver.resolve_speaker_source(
            speaker_label="speaker_user_me",
            speaker_id="spk-1",
            participant_id="part-1",
            source_id=0,
            has_local_mic_audio=True,
        )
        assert resolved.source_id == 0
        assert resolved.track_type == "local_mic"
        assert resolved.is_valid is True
        assert resolved.attribution_confidence >= 0.95

    def test_resolve_remote_participant(self):
        """Remote diarized speaker uses remote_mix (source 1)."""
        resolver = SpeakerAudioResolver()
        resolved: ResolvedSpeakerAudio = resolver.resolve_speaker_source(
            speaker_label="speaker_002",
            speaker_id="spk-2",
            participant_id="part-2",
            source_id=1,
            diarization_confidence=0.88,
        )
        assert resolved.source_id == 1
        assert resolved.track_type == "remote_mix"
        assert resolved.is_valid is True
        assert resolved.attribution_confidence == 0.88

    def test_resolve_uncertain_diarization_confidence(self):
        """Low diarization confidence (< 0.60) flags speaker as uncertain."""
        resolver = SpeakerAudioResolver()
        resolved: ResolvedSpeakerAudio = resolver.resolve_speaker_source(
            speaker_label="speaker_003",
            speaker_id="spk-3",
            participant_id="part-3",
            source_id=1,
            diarization_confidence=0.45,
        )
        assert resolved.is_valid is False
        assert "LOW_DIARIZATION_CONFIDENCE" in (resolved.exclusion_reason or "")
