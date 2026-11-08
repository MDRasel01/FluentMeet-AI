"""
FluentMeet AI - Step 08: Sentence Structure & Syntactic Variety Module
Evaluates sentence complexity, clause coordination/subordination, run-on detection,
and fragments.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.analysis.preprocessing.cleaner import CleanedSegment
from app.analysis.preprocessing.context import MeetingContext
from app.analysis.gemini.client import GeminiClient
from app.analysis.gemini.prompts import SYSTEM_INSTRUCTION, SENTENCE_STRUCTURE_PROMPT_TEMPLATE


@dataclass
class StructureObservation:
    segment_id: str
    issue_type: str  # run_on, fragment, repetitive_structure, awkward_coordination
    original_text: str
    improved_text: str
    explanation: str
    severity: str  # minor, moderate, major
    confidence: float


SUBORDINATE_CONJUNCTIONS = {
    "because", "although", "though", "even though", "while", "whereas",
    "since", "unless", "if", "provided that", "as long as", "in order that"
}

TRANSITIONAL_ADVERBS = {
    "however", "therefore", "furthermore", "moreover", "consequently",
    "meanwhile", "nevertheless", "subsequently"
}


class SentenceStructureAnalyzer:
    """
    Analyzes syntactic complexity, variety of clause coordination, and run-on sentences.
    """

    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        self.gemini = gemini_client or GeminiClient()

    async def analyze(
        self,
        speaker_label: str,
        segments: List[CleanedSegment],
        context: MeetingContext,
    ) -> Dict[str, Any]:
        """
        Analyzes syntactic variety and identifies run-ons or fragmented expressions.
        """
        if not segments:
            return {
                "observations": [],
                "score": 100.0,
                "status": "insufficient_data",
                "summary": "No segments available for sentence structure analysis.",
            }

        observations: List[StructureObservation] = []
        seen_keys = set()

        # 1. Heuristic check: detect conversational run-ons with 3+ 'and/then/so' chains in a single segment
        for seg in segments:
            text = seg.cleaned_text
            # Count coordinate conjunction chains
            coords = len(re.findall(r"\b(and\s+then|and|so\s+then)\b", text, re.IGNORECASE))
            words = seg.word_count
            if words > 25 and coords >= 3:
                key = (seg.segment_id, "run_on")
                if key not in seen_keys:
                    seen_keys.add(key)
                    observations.append(
                        StructureObservation(
                            segment_id=seg.segment_id,
                            issue_type="run_on",
                            original_text=text[:120] + ("..." if len(text) > 120 else ""),
                            improved_text="Divide into two distinct sentences to clarify cause and effect.",
                            explanation="Chaining multiple independent clauses with 'and' or 'so then' weakens clarity.",
                            severity="minor",
                            confidence=0.92,
                        )
                    )

        # 2. Count complex transitions & subordinations across speaker's transcript
        subordinate_count = 0
        transition_count = 0
        for seg in segments:
            lower = seg.cleaned_text.lower()
            for sub in SUBORDINATE_CONJUNCTIONS:
                if re.search(rf"\b{re.escape(sub)}\b", lower):
                    subordinate_count += 1
            for trans in TRANSITIONAL_ADVERBS:
                if re.search(rf"\b{re.escape(trans)}\b", lower):
                    transition_count += 1

        # 3. Call Gemini for deeper sentence structure intelligence
        gemini_score = 85.0
        summary = "Sentence structure analysis completed."

        try:
            formatted_segs = GeminiClient.format_segments_for_prompt(segments)
            prompt = SENTENCE_STRUCTURE_PROMPT_TEMPLATE.format(
                speaker_label=speaker_label,
                register=context.primary_register,
                formality_level=context.formality_level,
                segments_block=formatted_segs,
            )

            result = await self.gemini.generate_json(
                system_instruction=SYSTEM_INSTRUCTION,
                user_prompt=prompt,
                temperature=0.1,
            )

            gemini_obs = result.get("observations", [])
            gemini_score = float(result.get("structure_score", 85.0))
            summary = result.get("summary", summary)

            valid_segment_ids = {s.segment_id for s in segments}
            for item in gemini_obs:
                seg_id = str(item.get("segment_id", ""))
                if seg_id not in valid_segment_ids:
                    continue

                orig = item.get("original_text", "").strip()
                if not orig:
                    continue

                key = (seg_id, item.get("issue_type", "run_on"))
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                observations.append(
                    StructureObservation(
                        segment_id=seg_id,
                        issue_type=item.get("issue_type", "run_on"),
                        original_text=orig,
                        improved_text=item.get("improved_text", ""),
                        explanation=item.get("explanation", "Sentence restructuring suggestion"),
                        severity=item.get("severity", "minor"),
                        confidence=float(item.get("confidence", 0.90)),
                    )
                )

        except Exception as e:
            summary = f"Sentence structure analyzed via clause heuristic (AI fallback: {e})"

        # Calculate final sentence structure score
        total_words = sum(s.word_count for s in segments)
        if total_words < 20:
            final_score = 85.0
        else:
            variety_bonus = min(15.0, (subordinate_count + transition_count) * 2.5)
            penalty = len(observations) * 3.5
            stat_score = max(50.0, min(100.0, 80.0 + variety_bonus - penalty))
            final_score = round(0.4 * stat_score + 0.6 * gemini_score, 1)

        return {
            "observations": observations,
            "score": final_score,
            "status": "available",
            "evidence_count": len(observations),
            "summary": summary,
        }

