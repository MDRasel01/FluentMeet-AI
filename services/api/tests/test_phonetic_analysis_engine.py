"""
FluentMeet AI - Step 09 Test Suite: Phonetic Analysis Engine
Specification: Step 09 - Section 8, 9
"""

import pytest
import numpy as np
from app.pronunciation.alignment.word_aligner import AlignedWordAudio
from app.pronunciation.acoustic.phonetics import (
    PhoneticAnalysisEngine,
    REFERENCE_LEXICON,
    fallback_g2p,
    WordPronunciationEvidence,
)


class TestPhoneticAnalysisEngine:
    def test_lexicon_lookup_and_fallback_g2p(self):
        engine = PhoneticAnalysisEngine()

        # Word in CMU reference lexicon
        assert "think" in REFERENCE_LEXICON
        ipa, phonemes = REFERENCE_LEXICON["think"]
        assert "TH" in phonemes
        assert "NG" in phonemes

        # Word not in reference lexicon uses rule-based G2P fallback
        ipa_fb, phonemes_fb = fallback_g2p("cybersecurity")
        assert len(phonemes_fb) > 0
        assert ipa_fb.startswith("/")

    def test_analyze_word_with_clean_fricative_acoustic_evidence(self):
        """High frequency spectral presence confirms correct fricative articulation (/θ/)."""
        engine = PhoneticAnalysisEngine()
        sample_rate = 16000

        # Construct synthetic word PCM with high frequency energy (> 2500Hz) simulating voiceless fricative
        t = np.linspace(0, 0.3, int(sample_rate * 0.3), False)
        hf_signal = 0.4 * np.sin(2 * np.pi * 3500 * t) + 0.3 * np.random.normal(0, 0.5, len(t))
        pcm_bytes = (hf_signal * 16384).astype(np.int16).tobytes()

        aligned = AlignedWordAudio(
            word="think",
            clean_word="think",
            start_time_ms=1000,
            end_time_ms=1300,
            duration_ms=300,
            segment_id="seg-1",
            audio_storage_key="test.pcm",
            speaker_label="speaker_001",
            confidence=0.92,
            alignment_status="aligned",
            exclusion_reason=None,
            audio_pcm_slice=pcm_bytes,
        )

        evidence: WordPronunciationEvidence = engine.analyze_word(aligned, sample_rate=sample_rate)

        assert evidence.evaluation_status == "evaluated"
        assert evidence.expected_phonemes == "TH IH NG K"
        assert evidence.pronunciation_score >= 80.0
        assert len(evidence.phonemes) == 4

        # Check TH phoneme observation
        th_obs = next(p for p in evidence.phonemes if p.phoneme_reference == "TH")
        assert th_obs.issue_type == "correct"
        assert th_obs.phoneme_score >= 85.0

    def test_analyze_word_dental_fricative_substitution_detection(self):
        """Lack of high frequency energy during /θ/ triggers substitution warning (e.g. /t/ or /s/ stopping)."""
        engine = PhoneticAnalysisEngine()
        sample_rate = 16000

        # Low frequency only (e.g., 200Hz stop/plosive burst without fricative friction)
        t = np.linspace(0, 0.3, int(sample_rate * 0.3), False)
        lf_signal = 0.5 * np.sin(2 * np.pi * 200 * t)
        pcm_bytes = (lf_signal * 16384).astype(np.int16).tobytes()

        aligned = AlignedWordAudio(
            word="think",
            clean_word="think",
            start_time_ms=1000,
            end_time_ms=1300,
            duration_ms=300,
            segment_id="seg-1",
            audio_storage_key="test.pcm",
            speaker_label="speaker_001",
            confidence=0.85,
            alignment_status="aligned",
            exclusion_reason=None,
            audio_pcm_slice=pcm_bytes,
        )

        evidence = engine.analyze_word(aligned, sample_rate=sample_rate)

        th_obs = next(p for p in evidence.phonemes if p.phoneme_reference == "TH")
        assert th_obs.issue_type == "substitution"
        assert th_obs.phoneme_score < 75.0
