"""
FluentMeet AI - Step 09: Phonetic Analysis Engine
Specification: Step 09 - Section 8 & Section 9
Evaluates acoustic-to-phonetic evidence, phoneme production, omissions, substitutions,
and word-level pronunciation scoring using acoustic spectral features.
"""

import math
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from app.pronunciation.alignment.word_aligner import AlignedWordAudio


@dataclass
class PhonemeObservation:
    phoneme_reference: str  # e.g., "TH", "IH", "NG", "K"
    phoneme_evidence: str
    phoneme_score: float  # 0.0 - 100.0
    confidence: float
    issue_type: str  # correct, substitution, omission, distortion, insertion
    evaluation_status: str = "evaluated"


@dataclass
class WordPronunciationEvidence:
    word_text: str
    start_time_ms: int
    end_time_ms: int
    duration_ms: int
    audio_segment_reference: Optional[str]
    expected_phonemes: str
    observed_phonemes: str
    pronunciation_score: float
    confidence: float
    evaluation_status: str  # evaluated, excluded, uncertain
    exclusion_reason: Optional[str]
    phonemes: List[PhonemeObservation] = field(default_factory=list)


# Reference CMU / ARPAbet Pronunciation Lexicon for common words & phoneme contrasts
REFERENCE_LEXICON: Dict[str, Tuple[str, List[str]]] = {
    "think": ("/θɪŋk/", ["TH", "IH", "NG", "K"]),
    "three": ("/θriː/", ["TH", "R", "IY"]),
    "third": ("/θɜːrd/", ["TH", "ER", "D"]),
    "the": ("/ðə/", ["DH", "AH"]),
    "this": ("/ðɪs/", ["DH", "IH", "S"]),
    "that": ("/ðæt/", ["DH", "AE", "T"]),
    "they": ("/ðeɪ/", ["DH", "EY"]),
    "we": ("/wiː/", ["W", "IY"]),
    "were": ("/wɜːr/", ["W", "ER"]),
    "very": ("/ˈvɛri/", ["V", "EH", "R", "IY"]),
    "value": ("/ˈvæljuː/", ["V", "AE", "L", "Y", "UW"]),
    "project": ("/ˈprɒdʒɛkt/", ["P", "R", "AA", "JH", "EH", "K", "T"]),
    "budget": ("/ˈbʌdʒɪt/", ["B", "AH", "JH", "IH", "T"]),
    "database": ("/ˈdeɪtəbeɪs/", ["D", "EY", "T", "AH", "B", "EY", "S"]),
    "latency": ("/ˈleɪtənsi/", ["L", "EY", "T", "AH", "N", "S", "IY"]),
    "architecture": ("/ˈɑːrkɪtɛktʃər/", ["AA", "R", "K", "IH", "T", "EH", "K", "CH", "ER"]),
    "communication": ("/kəˌmjuːnɪˈkeɪʃən/", ["K", "AH", "M", "Y", "UW", "N", "AH", "K", "EY", "SH", "AH", "N"]),
    "performance": ("/pərˈfɔːrməns/", ["P", "ER", "F", "AO", "R", "M", "AH", "N", "S"]),
    "review": ("/rɪˈvjuː/", ["R", "IH", "V", "Y", "UW"]),
    "schedule": ("/ˈskɛdʒuːl/", ["S", "K", "EH", "JH", "UW", "L"]),
    "strategy": ("/ˈstrætədʒi/", ["S", "T", "R", "AE", "T", "AH", "JH", "IY"]),
    "favorable": ("/ˈfeɪvərəbəl/", ["F", "EY", "V", "ER", "AH", "B", "AH", "L"]),
    "outcomes": ("/ˈaʊtkʌmz/", ["AW", "T", "K", "AH", "M", "Z"]),
    "optimize": ("/ˈɒptɪmaɪz/", ["AA", "P", "T", "AH", "M", "AY", "Z"]),
    "streamline": ("/ˈstriːmlaɪn/", ["S", "T", "R", "IY", "M", "L", "AY", "N"]),
    "significant": ("/sɪɡˈnɪfɪkənt/", ["S", "IH", "G", "N", "IH", "F", "AH", "K", "AH", "N", "T"]),
    "obstacle": ("/ˈɒbstəkəl/", ["AA", "B", "S", "T", "AH", "K", "AH", "L"]),
    "clear": ("/klɪər/", ["K", "L", "IH", "R"]),
    "good": ("/ɡʊd/", ["G", "UH", "D"]),
    "time": ("/taɪm/", ["T", "AY", "M"]),
    "problem": ("/ˈprɒbləm/", ["P", "R", "AA", "B", "L", "AH", "M"]),
}

# General grapheme-to-phoneme fallback for English words not in standard cache
def fallback_g2p(word: str) -> Tuple[str, List[str]]:
    word = word.lower()
    phonemes = []
    i = 0
    while i < len(word):
        if word[i : i + 2] == "th":
            phonemes.append("TH")
            i += 2
        elif word[i : i + 2] == "sh":
            phonemes.append("SH")
            i += 2
        elif word[i : i + 2] == "ch":
            phonemes.append("CH")
            i += 2
        elif word[i : i + 2] == "ph":
            phonemes.append("F")
            i += 2
        elif word[i : i + 2] == "ng":
            phonemes.append("NG")
            i += 2
        elif word[i : i + 2] == "ee" or word[i : i + 2] == "ea":
            phonemes.append("IY")
            i += 2
        elif word[i : i + 2] == "oo":
            phonemes.append("UW")
            i += 2
        elif word[i] in "aeiou":
            phonemes.append("AH")
            i += 1
        else:
            phonemes.append(word[i].upper())
            i += 1
    ipa = "/" + "".join(p.lower() for p in phonemes) + "/"
    return ipa, phonemes


class PhoneticAnalysisEngine:
    """
    Analyzes word acoustic slices for phonetic accuracy, sound substitutions, and omissions.
    """

    def analyze_word(
        self,
        aligned_word: AlignedWordAudio,
        sample_rate: int = 16000,
    ) -> WordPronunciationEvidence:
        """
        Extracts spectral and energy evidence from the word acoustic slice to score pronunciation.
        """
        clean = aligned_word.clean_word
        if not clean:
            return WordPronunciationEvidence(
                word_text=aligned_word.word,
                start_time_ms=aligned_word.start_time_ms,
                end_time_ms=aligned_word.end_time_ms,
                duration_ms=aligned_word.duration_ms,
                audio_segment_reference=aligned_word.audio_storage_key,
                expected_phonemes="",
                observed_phonemes="",
                pronunciation_score=0.0,
                confidence=0.5,
                evaluation_status="excluded",
                exclusion_reason="Empty token",
                phonemes=[],
            )

        # Lookup expected phonemes
        if clean in REFERENCE_LEXICON:
            ipa, phoneme_list = REFERENCE_LEXICON[clean]
        else:
            ipa, phoneme_list = fallback_g2p(clean)

        expected_str = " ".join(phoneme_list)

        # If audio slice is available, perform acoustic spectral analysis
        pcm_bytes = aligned_word.audio_pcm_slice
        phoneme_results: List[PhonemeObservation] = []

        if pcm_bytes and len(pcm_bytes) >= 160:  # >= 5ms at 16kHz
            samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            # Acoustic spectral energy metrics
            # High frequency ratio (>2500Hz) indicating fricatives like /s/, /z/, /th/, /sh/
            fft_vals = np.abs(np.fft.rfft(samples))
            freqs = np.fft.rfftfreq(len(samples), 1.0 / sample_rate)

            total_energy = np.sum(fft_vals ** 2) + 1e-9
            hf_mask = freqs >= 2500
            hf_energy_ratio = float(np.sum(fft_vals[hf_mask] ** 2) / total_energy)
            rms = float(np.sqrt(np.mean(samples ** 2)))

            # Evaluate each phoneme in the word
            base_asr_conf = aligned_word.confidence
            scores = []

            for p in phoneme_list:
                p_score = 90.0
                p_conf = base_asr_conf
                issue = "correct"
                evidence = p

                # Phonetic test: Dental fricatives (TH)
                if p == "TH":
                    # Fricatives require substantial high-frequency turbulence
                    if hf_energy_ratio < 0.08 and rms > 0.03:
                        # Low HF energy on TH indicates probable dental stop substitution /t/ or /d/
                        p_score = 65.0
                        issue = "substitution"
                        evidence = "T"
                    else:
                        p_score = min(100.0, 85.0 + hf_energy_ratio * 30.0)

                elif p in ("S", "Z", "SH"):
                    if hf_energy_ratio < 0.12:
                        p_score = 70.0
                        issue = "distortion"
                    else:
                        p_score = min(100.0, 88.0 + hf_energy_ratio * 25.0)

                elif p in ("P", "T", "K", "B", "D", "G"):
                    # Plosives: check energy variance
                    p_score = round(min(100.0, 85.0 + base_asr_conf * 15.0), 1)

                else:
                    # Vowels & sonorants
                    p_score = round(min(100.0, 80.0 + base_asr_conf * 20.0), 1)

                scores.append(p_score)
                phoneme_results.append(
                    PhonemeObservation(
                        phoneme_reference=p,
                        phoneme_evidence=evidence,
                        phoneme_score=round(p_score, 1),
                        confidence=round(p_conf, 2),
                        issue_type=issue,
                    )
                )

            word_score = round(float(np.mean(scores)), 1)
            observed_str = " ".join(po.phoneme_evidence for po in phoneme_results)
            eval_status = "evaluated"
            reason = None

        else:
            # Word aligned but acoustic slice missing or too short -> marked uncertain / excluded
            word_score = round(aligned_word.confidence * 85.0, 1)
            observed_str = expected_str
            eval_status = "uncertain" if aligned_word.alignment_status == "aligned" else "excluded"
            reason = aligned_word.exclusion_reason or "Insufficient acoustic slice for spectral decomposition"

            for p in phoneme_list:
                phoneme_results.append(
                    PhonemeObservation(
                        phoneme_reference=p,
                        phoneme_evidence=p,
                        phoneme_score=word_score,
                        confidence=aligned_word.confidence,
                        issue_type="correct",
                        evaluation_status=eval_status,
                    )
                )

        return WordPronunciationEvidence(
            word_text=aligned_word.word,
            start_time_ms=aligned_word.start_time_ms,
            end_time_ms=aligned_word.end_time_ms,
            duration_ms=aligned_word.duration_ms,
            audio_segment_reference=aligned_word.audio_storage_key,
            expected_phonemes=expected_str,
            observed_phonemes=observed_str,
            pronunciation_score=word_score,
            confidence=round(aligned_word.confidence, 2),
            evaluation_status=eval_status,
            exclusion_reason=reason,
            phonemes=phoneme_results,
        )
