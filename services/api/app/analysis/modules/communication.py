"""
FluentMeet AI - Step 08: Communication Intelligence Module
Assesses communicative effectiveness, active listening, conversational diplomacy,
and professional tone.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.analysis.preprocessing.cleaner import CleanedSegment
from app.analysis.preprocessing.context import MeetingContext
from app.analysis.gemini.client import GeminiClient
from app.analysis.gemini.prompts import SYSTEM_INSTRUCTION, COMMUNICATION_PROMPT_TEMPLATE


@dataclass
class CommunicationInsightItem:
    insight_type: str  # response_relevance, active_listening, conversation_management, professional_tone, clarity
    title: str
    description: str
    evidence: Optional[str]
    confidence: float


ACTIVE_LISTENING_PATTERNS = [
    r"\b(i agree with|to follow up on|what you said|as you mentioned|good point|that makes sense|could you clarify)\b",
    r"\b(from my understanding|if i understand correctly|building on that)\b"
]

PROFESSIONAL_DIPLOMACY_PATTERNS = [
    r"\b(perhaps we could|would it be possible|i would suggest|in my view|from our perspective)\b"
]


class CommunicationAnalyzer:
    """
    Evaluates conversational diplomacy, active listening, and communicative effectiveness.
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
        Analyzes communicative competencies and dialogue dynamics.
        """
        if not segments:
            return {
                "insights": [],
                "score": 100.0,
                "status": "insufficient_data",
                "summary": "No segments available for communication analysis.",
            }

        insights: List[CommunicationInsightItem] = []

        # 1. Check active listening markers locally
        full_text = " ".join(s.cleaned_text for s in segments)
        active_listening_hits = 0
        for pat in ACTIVE_LISTENING_PATTERNS:
            matches = re.findall(pat, full_text, re.IGNORECASE)
            active_listening_hits += len(matches)

        if active_listening_hits > 0:
            insights.append(
                CommunicationInsightItem(
                    insight_type="active_listening",
                    title="Active Listening & Collaborative Dialogue",
                    description=f"Demonstrated collaborative engagement by explicitly referencing colleagues' points ({active_listening_hits} markers detected).",
                    evidence=f"Active listening markers present throughout discussion.",
                    confidence=0.95,
                )
            )

        # 2. Check professional tone & diplomacy
        diplomacy_hits = 0
        for pat in PROFESSIONAL_DIPLOMACY_PATTERNS:
            matches = re.findall(pat, full_text, re.IGNORECASE)
            diplomacy_hits += len(matches)

        if diplomacy_hits > 0:
            insights.append(
                CommunicationInsightItem(
                    insight_type="professional_tone",
                    title="Diplomatic & Consultative Tone",
                    description="Utilized polite hedging and constructive framing to invite consensus.",
                    evidence=f"Framed suggestions diplomatically using consultative phrasing.",
                    confidence=0.92,
                )
            )

        # 3. Call Gemini for deeper communication intelligence
        gemini_score = 88.0
        summary = "Communication analysis completed."

        try:
            formatted_segs = GeminiClient.format_segments_for_prompt(segments)
            prompt = COMMUNICATION_PROMPT_TEMPLATE.format(
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
            gemini_score = float(result.get("communication_score", 88.0))
            summary = result.get("summary", summary)

            for item in gemini_insights:
                title = item.get("title", "").strip()
                if not title:
                    continue
                insights.append(
                    CommunicationInsightItem(
                        insight_type=item.get("insight_type", "clarity"),
                        title=title,
                        description=item.get("description", ""),
                        evidence=item.get("evidence"),
                        confidence=float(item.get("confidence", 0.90)),
                    )
                )

        except Exception as e:
            summary = f"Communication evaluated via engagement patterns (AI fallback: {e})"

        # Deduce final communication score
        bonus = min(10.0, (active_listening_hits + diplomacy_hits) * 3.0)
        heuristic_score = min(100.0, 80.0 + bonus)
        final_score = round(0.4 * heuristic_score + 0.6 * gemini_score, 1)

        return {
            "insights": insights,
            "score": final_score,
            "status": "available",
            "evidence_count": len(insights),
            "summary": summary,
        }

