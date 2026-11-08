"""
FluentMeet AI - Step 09: Pronunciation Recommendation Generator
Specification: Step 09 - Section 15
Generates concrete, actionable pronunciation drills: minimal pairs, syllable stress,
and intonation modulation linked directly to acoustic findings.
"""

from typing import List, Dict, Any, Optional
from collections import Counter
from dataclasses import dataclass

from app.pronunciation.acoustic.phonetics import WordPronunciationEvidence
from app.pronunciation.acoustic.prosody import ProsodyReport
from app.pronunciation.acoustic.pace import SpeakingPaceReport


@dataclass
class PronunciationExercise:
    category: str  # phoneme, minimal_pair, word_stress, sentence_stress, intonation, speaking_pace, connected_speech
    title: str
    description: str
    evidence_reference: Optional[str]
    expected_pronunciation: Optional[str]
    suggested_exercise: str
    priority: str  # high, medium, low
    difficulty_level: str  # beginner, intermediate, advanced
    confidence: float


# Curated minimal pair exercise database for common ESL phonetic substitutions
MINIMAL_PAIR_EXERCISES = {
    "TH": {
        "title": "Voiceless Dental Fricative (/θ/) Minimal Pairs",
        "description": "Practice placing the tongue tip between upper and lower teeth with continuous airflow rather than a stopping /t/ sound.",
        "pairs": ["think / sink", "three / tree", "thin / tin", "thought / taught"],
        "expected": "/θ/ (tongue between teeth, friction airflow)",
    },
    "DH": {
        "title": "Voiced Dental Fricative (/ð/) Minimal Pairs",
        "description": "Vibrate vocal cords while tongue is gently pressed against upper front teeth.",
        "pairs": ["they / day", "then / den", "there / dare", "breathe / breed"],
        "expected": "/ð/ (voiced dental fricative)",
    },
    "V": {
        "title": "Labiodental Fricative (/v/ vs /w/) Contrast",
        "description": "Touch upper teeth lightly to lower lip for /v/; round lips forward for /w/.",
        "pairs": ["very / wary", "vine / wine", "vest / west", "value / whale"],
        "expected": "/v/ vs /w/ distinction",
    },
}


class PronunciationRecommendationGenerator:
    """
    Synthesizes detected acoustic weaknesses into targeted learner-friendly drills.
    """

    def generate_recommendations(
        self,
        word_evidences: List[WordPronunciationEvidence],
        prosody: ProsodyReport,
        pace: SpeakingPaceReport,
    ) -> List[PronunciationExercise]:
        """
        Produces prioritized practice exercises.
        """
        recommendations: List[PronunciationExercise] = []

        # 1. Phonetic Substitutions (e.g. TH substitutions)
        phoneme_issues = [
            (p.phoneme_reference, p.phoneme_evidence, w.word_text)
            for w in word_evidences
            for p in w.phonemes
            if p.issue_type in ("substitution", "distortion")
        ]

        if phoneme_issues:
            ref_counts = Counter(item[0] for item in phoneme_issues)
            top_phoneme, count = ref_counts.most_common(1)[0]

            if top_phoneme in MINIMAL_PAIR_EXERCISES:
                mp = MINIMAL_PAIR_EXERCISES[top_phoneme]
                affected_words = list({item[2] for item in phoneme_issues if item[0] == top_phoneme})[:3]
                recommendations.append(
                    PronunciationExercise(
                        category="minimal_pair",
                        title=mp["title"],
                        description=mp["description"],
                        evidence_reference=f"Observed in words: {', '.join(affected_words)}",
                        expected_pronunciation=mp["expected"],
                        suggested_exercise=f"Practice minimal pairs aloud: {', '.join(mp['pairs'])}.",
                        priority="high" if count >= 2 else "medium",
                        difficulty_level="intermediate",
                        confidence=0.92,
                    )
                )

        # 2. Speaking Pace & Rushed Delivery
        if pace.wpm > 170.0:
            recommendations.append(
                PronunciationExercise(
                    category="speaking_pace",
                    title="Speaking Pace Modulation for Acoustic Articulation",
                    description=(
                        f"Your current speaking pace is {pace.wpm:.0f} WPM. Rapid articulation causes "
                        "final consonant clusters to compress. Intentionally pacing your sentences allows clearer phonetic boundaries."
                    ),
                    evidence_reference=f"Recorded speech pace: {pace.wpm:.0f} WPM across session.",
                    expected_pronunciation="130 - 160 WPM benchmark",
                    suggested_exercise="Read a 50-word technical paragraph using a metronome or stopwatch set for 20 seconds.",
                    priority="high" if pace.wpm > 185 else "medium",
                    difficulty_level="beginner",
                    confidence=0.95,
                )
            )
        elif pace.wpm < 100.0:
            recommendations.append(
                PronunciationExercise(
                    category="speaking_pace",
                    title="Developing Speech Rhythm and Momentum",
                    description=(
                        f"Your speech rate is {pace.wpm:.0f} WPM with pauses averaging {pace.pause_metrics.get('avg_pause_ms', 0)}ms. "
                        "Linking function words to content words creates natural spoken momentum."
                    ),
                    evidence_reference=f"Recorded speech pace: {pace.wpm:.0f} WPM.",
                    expected_pronunciation="125 - 150 WPM benchmark",
                    suggested_exercise="Practice shadow reading a 1-minute audio recording to match natural linking.",
                    priority="medium",
                    difficulty_level="intermediate",
                    confidence=0.92,
                )
            )

        # 3. Word & Syllable Stress
        if prosody.word_stress_score < 80.0:
            recommendations.append(
                PronunciationExercise(
                    category="word_stress",
                    title="Multi-Syllable Word Stress Placement",
                    description=(
                        "Lengthen and slightly raise the pitch of the primary stressed syllable in technical vocabulary "
                        "while reducing unstressed vowels to schwa (/ə/)."
                    ),
                    evidence_reference="Observed compressed acoustic energy variance across multi-syllable terms.",
                    expected_pronunciation="Primary stressed syllable: longer duration + higher pitch",
                    suggested_exercise="Contrast noun-verb stress pairs: 'PRÓ-ject' (noun) vs 'pro-JÉCT' (verb).",
                    priority="medium",
                    difficulty_level="intermediate",
                    confidence=0.88,
                )
            )

        # 4. Intonation Dynamics
        if prosody.intonation_score < 80.0:
            recommendations.append(
                PronunciationExercise(
                    category="intonation",
                    title="Sentence-Final Pitch Contour Cadence",
                    description=(
                        "Allow pitch to fall clearly at the end of declarative statements to convey finality and authority. "
                        "Avoid upward pitch inflections on routine updates."
                    ),
                    evidence_reference=f"Pitch range: {prosody.pitch_features.pitch_range_hz:.0f}Hz ({prosody.pitch_features.contour_type} contour).",
                    expected_pronunciation="Steep downward pitch step at period boundaries",
                    suggested_exercise="Practice speaking 3 statements ensuring your voice drops naturally on the final word.",
                    priority="low",
                    difficulty_level="beginner",
                    confidence=0.85,
                )
            )

        # Priority sorting: high first, then medium, then low
        prio_map = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: prio_map.get(r.priority, 3))
        return recommendations[:5]
