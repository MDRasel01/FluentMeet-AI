"""
FluentMeet AI - Step 08: Context & Register Detection
Analyzes the transcript to classify the meeting register (Business, Technical, Interview, Client, Casual)
and extract domain vocabulary for calibrated linguistic scoring.
"""

import re
from typing import List, Dict, Any, Set
from dataclasses import dataclass, field


@dataclass
class MeetingContext:
    primary_register: str  # business, technical, interview, client_discussion, casual
    confidence: float  # 0.0 - 1.0
    detected_terms: List[str] = field(default_factory=list)
    register_scores: Dict[str, float] = field(default_factory=dict)
    formality_level: str = "semi_formal"  # formal, semi_formal, casual


class ContextDetector:
    """
    Identifies communication context and register from meeting transcripts.
    """

    LEXICONS: Dict[str, Set[str]] = {
        "business": {
            "agenda", "deliverable", "deliverables", "stakeholder", "stakeholders", "timeline",
            "kpi", "milestone", "milestones", "budget", "quarter", "roi", "revenue", "strategy",
            "roadmap", "action item", "action items", "alignment", "bandwidth", "synergy",
            "objective", "objectives", "priority", "priorities", "workflow", "governance"
        },
        "technical": {
            "api", "architecture", "database", "backend", "frontend", "docker", "kubernetes",
            "endpoint", "endpoints", "refactor", "latency", "deployment", "bug", "bugs",
            "git", "commit", "ci/cd", "pipeline", "schema", "microservice", "infrastructure",
            "query", "cache", "redis", "postgres", "asynchronous", "thread", "payload"
        },
        "interview": {
            "experience", "background", "resume", "position", "career", "qualification",
            "strengths", "weakness", "weaknesses", "tell me about yourself", "salary",
            "compensation", "previous role", "challenge", "accomplishment", "portfolio",
            "notice period", "skillset", "leadership style"
        },
        "client_discussion": {
            "contract", "proposal", "requirement", "requirements", "scope", "pricing",
            "sla", "onboarding", "demo", "demonstration", "feedback", "client", "customer",
            "deliverable", "support", "agreement", "sign-off", "implementation"
        },
        "casual": {
            "weekend", "weather", "coffee", "catch up", "funny", "vacation", "holiday",
            "lunch", "relax", "hang out", "chatted", "how's it going", "what's up",
            "movies", "family", "traffic"
        },
    }

    def detect_context(self, full_text: str) -> MeetingContext:
        """
        Analyzes the full transcript text to detect primary register and key domain terminology.
        """
        if not full_text:
            return MeetingContext(
                primary_register="business",
                confidence=0.5,
                detected_terms=[],
                register_scores={"business": 0.5},
                formality_level="semi_formal",
            )

        lower_text = full_text.lower()
        # Tokenize into words and 2-grams
        words = re.findall(r"\b[a-z0-9_-]+\b", lower_text)
        word_set = set(words)
        bigrams = {f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)}
        combined_tokens = word_set.union(bigrams)

        scores: Dict[str, float] = {}
        all_detected: Dict[str, List[str]] = {}

        for reg, lexicon in self.LEXICONS.items():
            matches = [term for term in lexicon if term in combined_tokens or (f" {term} " in f" {lower_text} ")]
            all_detected[reg] = matches
            # Weight matches: count of matching terms normalized by lexicon size
            score = len(matches) / max(1, len(lexicon))
            scores[reg] = score

        # Determine winner
        best_reg = "business"
        best_score = 0.0

        # Give slight baseline preference to business in corporate SaaS if tied
        for reg, score in scores.items():
            if score > best_score:
                best_score = score
                best_reg = reg

        # If no significant domain terms found, default to general business/semi-formal
        if best_score < 0.05:
            best_reg = "business"
            conf = 0.5
            formality = "semi_formal"
            detected = []
        else:
            # Calibrate confidence based on score margin
            conf = min(0.95, max(0.55, best_score * 2.5))
            detected = all_detected.get(best_reg, [])
            if best_reg in ("interview", "client_discussion"):
                formality = "formal"
            elif best_reg == "casual":
                formality = "casual"
            else:
                formality = "semi_formal"

        return MeetingContext(
            primary_register=best_reg,
            confidence=round(conf, 2),
            detected_terms=detected[:15],
            register_scores={k: round(v, 3) for k, v in scores.items()},
            formality_level=formality,
        )

