"""
FluentMeet AI - Step 08: Vocabulary Intelligence Module
Calculates lexical diversity (MATTR), identifies overused phrases,
and provides context-aware business & technical collocation enhancements.
"""

import re
from typing import List, Dict, Any, Optional
from collections import Counter
from dataclasses import dataclass

from app.analysis.preprocessing.cleaner import CleanedSegment
from app.analysis.preprocessing.context import MeetingContext
from app.analysis.gemini.client import GeminiClient
from app.analysis.gemini.prompts import SYSTEM_INSTRUCTION, VOCABULARY_PROMPT_TEMPLATE


@dataclass
class VocabularyInsightItem:
    segment_id: str
    insight_type: str  # word_choice, overused, repetition, business_expression, collocation, precision
    original_expression: str
    suggested_expression: str
    explanation: str
    context_note: Optional[str]
    example_sentence: Optional[str]
    confidence: float


# Heuristic overused phrases with executive / professional alternatives
COMMON_VOCAB_ENHANCEMENTS = [
    {
        "pattern": r"\b(good\s+things|good\s+stuff)\b",
        "type": "word_choice",
        "replacement": "favorable outcomes",
        "explanation": "'Favorable outcomes' or 'valuable insights' projects executive presence rather than informal casual phrasing.",
        "example": "The pilot phase yielded favorable outcomes across all primary KPIs.",
    },
    {
        "pattern": r"\b(very\s+big\s+problem|big\s+issue)\b",
        "type": "precision",
        "replacement": "significant obstacle",
        "explanation": "'Significant obstacle' or 'critical bottleneck' is more precise and constructive.",
        "example": "We encountered a significant obstacle in the third-party API integration.",
    },
    {
        "pattern": r"\b(make\s+it\s+better)\b",
        "type": "business_expression",
        "replacement": "optimize / streamline",
        "explanation": "Verbs like 'optimize', 'enhance', or 'streamline' clearly communicate intentional progress.",
        "example": "Our immediate objective is to streamline the deployment workflow.",
    },
    {
        "pattern": r"\b(a\s+lot\s+of\s+things|a\s+lot\s+of\s+stuff)\b",
        "type": "overused",
        "replacement": "multiple initiatives / comprehensive elements",
        "explanation": "Specifying 'initiatives', 'components', or 'items' adds clarity.",
        "example": "We are juggling multiple initiatives ahead of the quarter-end release.",
    },
]


class VocabularyAnalyzer:
    """
    Evaluates lexical variety, Type-Token Ratio, and executive vocabulary enhancement.
    """

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        self.gemini = gemini_client or GeminiClient()

    @staticmethod
    def calculate_mattr(words: List[str], window_size: int = 50) -> float:
        """
        Calculates Moving-Average Type-Token Ratio (MATTR) across speech windows.
        Avoids text-length bias inherent in basic TTR.
        """
        if not words:
            return 0.0
        if len(words) <= window_size:
            return len(set(words)) / len(words)

        ttrs = []
        for i in range(len(words) - window_size + 1):
            window = words[i : i + window_size]
            ttrs.append(len(set(window)) / window_size)

        return sum(ttrs) / len(ttrs)

    async def analyze(
        self,
        speaker_label: str,
        segments: List[CleanedSegment],
        context: MeetingContext,
    ) -> Dict[str, Any]:
        """
        Analyzes lexical richness, MATTR, and produces tailored vocabulary recommendations.
        """
        if not segments:
            return {
                "insights": [],
                "score": 100.0,
                "status": "insufficient_data",
                "mattr": 0.0,
                "summary": "No segments available for vocabulary analysis.",
            }

        # Tokenize words for vocabulary analytics
        all_words: List[str] = []
        for seg in segments:
            tokens = re.findall(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b", seg.cleaned_text.lower())
            all_words.extend(tokens)

        total_words = len(all_words)
        unique_words = len(set(all_words))
        mattr = round(self.calculate_mattr(all_words), 3)

        insights: List[VocabularyInsightItem] = []
        seen_keys = set()

        # 1. Deterministic phrase check
        for seg in segments:
            text = seg.cleaned_text
            for rule in COMMON_VOCAB_ENHANCEMENTS:
                match = re.search(rule["pattern"], text, re.IGNORECASE)
                if match:
                    orig = match.group(0)
                    key = (seg.segment_id, orig.lower())
                    if key not in seen_keys:
                        seen_keys.add(key)
                        insights.append(
                            VocabularyInsightItem(
                                segment_id=seg.segment_id,
                                insight_type=rule["type"],
                                original_expression=orig,
                                suggested_expression=rule["replacement"],
                                explanation=rule["explanation"],
                                context_note=f"Context: {context.primary_register}",
                                example_sentence=rule["example"],
                                confidence=0.95,
                            )
                        )

        # 2. Call Gemini for contextual vocabulary enhancement
        gemini_score = 85.0
        summary = "Vocabulary assessment completed."

        try:
            formatted_segs = GeminiClient.format_segments_for_prompt(segments)
            prompt = VOCABULARY_PROMPT_TEMPLATE.format(
                speaker_label=speaker_label,
                register=context.primary_register,
                formality_level=context.formality_level,
                segments_block=formatted_segs,
            )

            result = await self.gemini.generate_json(
                system_instruction=SYSTEM_INSTRUCTION,
                user_prompt=prompt,
                temperature=0.2,
            )

            gemini_insights = result.get("insights", [])
            gemini_score = float(result.get("vocabulary_score", 85.0))
            summary = result.get("summary", summary)

            valid_segment_ids = {s.segment_id for s in segments}
            for item in gemini_insights:
                seg_id = str(item.get("segment_id", ""))
                if seg_id not in valid_segment_ids:
                    continue

                orig = item.get("original_expression", "").strip()
                if not orig:
                    continue

                key = (seg_id, orig.lower())
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                insights.append(
                    VocabularyInsightItem(
                        segment_id=seg_id,
                        insight_type=item.get("insight_type", "word_choice"),
                        original_expression=orig,
                        suggested_expression=item.get("suggested_expression", ""),
                        explanation=item.get("explanation", "Professional vocabulary enhancement"),
                        context_note=f"Register: {context.primary_register}",
                        example_sentence=item.get("example_sentence"),
                        confidence=float(item.get("confidence", 0.90)),
                    )
                )

        except Exception as e:
            summary = f"Vocabulary analyzed via lexical statistics (AI inference fallback: {e})"

        # Calculate final calibrated vocabulary score
        # MATTR typical ranges: <0.55 (limited/repetitive), 0.55-0.70 (healthy spoken), >0.70 (rich)
        if total_words < 20:
            vocab_stat_score = 80.0
        else:
            base_ttr_score = min(100.0, max(40.0, mattr * 130.0))
            # Slight deduction for each overused phrase
            penalty = len(insights) * 2.0
            vocab_stat_score = max(50.0, min(100.0, base_ttr_score - penalty))

        final_score = round(0.4 * vocab_stat_score + 0.6 * gemini_score, 1)

        return {
            "insights": insights,
            "score": final_score,
            "status": "available",
            "mattr": mattr,
            "total_words": total_words,
            "unique_words": unique_words,
            "evidence_count": len(insights),
            "summary": summary,
        }
