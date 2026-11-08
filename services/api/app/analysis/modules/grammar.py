"""
FluentMeet AI - Step 08: Grammar Intelligence Module
Combines Gemini LLM assessment with deterministic ESL rule patterns to detect,
classify, and correct grammatical errors with precise segment linking.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.analysis.preprocessing.cleaner import CleanedSegment
from app.analysis.preprocessing.context import MeetingContext
from app.analysis.gemini.client import GeminiClient
from app.analysis.gemini.prompts import SYSTEM_INSTRUCTION, GRAMMAR_PROMPT_TEMPLATE


@dataclass
class GrammarFinding:
    segment_id: str
    category: str  # tense, subject_verb_agreement, articles, prepositions, pronouns, sentence_construction, conditionals, modals, other
    original_text: str
    corrected_text: str
    explanation: str
    rule_name: str
    suggested_alternative: Optional[str]
    severity: str  # minor, moderate, major
    confidence: float
    evidence_status: str = "verified"


# Common deterministic ESL spoken patterns for high-precision local detection & fallback
ESL_PATTERNS = [
    {
        "pattern": r"\b(he|she|it)\s+(don't|dont)\b",
        "category": "subject_verb_agreement",
        "rule_name": "Third-Person Singular Present Agreement",
        "replacement": r"\1 doesn't",
        "explanation": "Third-person singular subjects ('he', 'she', 'it') take 'doesn't', not 'don't'.",
        "severity": "moderate",
    },
    {
        "pattern": r"\b(we|they|you)\s+was\b",
        "category": "subject_verb_agreement",
        "rule_name": "Past Tense Plural Agreement",
        "replacement": r"\1 were",
        "explanation": "Plural pronouns ('we', 'they', 'you') require the plural past verb 'were'.",
        "severity": "major",
    },
    {
        "pattern": r"\bdiscuss\s+about\b",
        "category": "prepositions",
        "rule_name": "Transitive Verb Preposition Redundancy",
        "replacement": "discuss",
        "explanation": "'Discuss' is a transitive verb that directly takes an object without the preposition 'about'.",
        "severity": "minor",
    },
    {
        "pattern": r"\bdepend\s+of\b",
        "category": "prepositions",
        "rule_name": "Dependent Preposition Collocation",
        "replacement": "depend on",
        "explanation": "The verb 'depend' takes the preposition 'on' or 'upon', not 'of'.",
        "severity": "moderate",
    },
    {
        "pattern": r"\b(didn't|did\s+not)\s+(went|saw|came|took|spoke)\b",
        "category": "tense",
        "rule_name": "Past Auxiliary with Base Verb Form",
        "replacement": "did not [base verb]",
        "explanation": "After the auxiliary 'did not / didn't', use the base infinitive form of the verb, not the past tense form.",
        "severity": "major",
    },
    {
        "pattern": r"\b(don't|didn't|can't|never)\s+have\s+no\b",
        "category": "other",
        "rule_name": "Double Negative Elimination",
        "replacement": "don't have any",
        "explanation": "Double negatives create confusion; use 'any' with negative auxiliary verbs.",
        "severity": "major",
    },
]


class GrammarAnalyzer:
    """
    Performs comprehensive grammar intelligence analysis on cleaned speaker segments.
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
        Analyzes grammar for a speaker across their segments.
        Returns list of GrammarFinding objects, overall score, and summary.
        """
        if not segments:
            return {
                "issues": [],
                "score": 100.0,
                "status": "insufficient_data",
                "summary": "No segments available for grammar analysis.",
            }

        # 1. First run deterministic ESL pattern pass on all segments
        findings: List[GrammarFinding] = []
        found_keys = set()

        for seg in segments:
            text = seg.cleaned_text
            for rule in ESL_PATTERNS:
                match = re.search(rule["pattern"], text, re.IGNORECASE)
                if match:
                    original = match.group(0)
                    key = (seg.segment_id, original.lower())
                    if key not in found_keys:
                        found_keys.add(key)
                        findings.append(
                            GrammarFinding(
                                segment_id=seg.segment_id,
                                category=rule["category"],
                                original_text=original,
                                corrected_text=re.sub(rule["pattern"], rule["replacement"], original, flags=re.IGNORECASE),
                                explanation=rule["explanation"],
                                rule_name=rule["rule_name"],
                                suggested_alternative=None,
                                severity=rule["severity"],
                                confidence=0.98,
                                evidence_status="verified",
                            )
                        )

        # 2. Call Gemini for contextual, nuanced, and complex grammar errors
        gemini_score = 90.0
        summary = "Grammar analysis completed."

        try:
            formatted_segs = GeminiClient.format_segments_for_prompt(segments)
            prompt = GRAMMAR_PROMPT_TEMPLATE.format(
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

            gemini_issues = result.get("issues", [])
            gemini_score = float(result.get("grammar_score", 88.0))
            summary = result.get("summary", summary)

            # Map Gemini issues
            valid_segment_ids = {s.segment_id for s in segments}
            for item in gemini_issues:
                seg_id = str(item.get("segment_id", ""))
                # Validate segment ID exists in this speaker's segments
                if seg_id not in valid_segment_ids:
                    continue

                orig = item.get("original_text", "").strip()
                if not orig:
                    continue

                key = (seg_id, orig.lower())
                if key in found_keys:
                    continue
                found_keys.add(key)

                findings.append(
                    GrammarFinding(
                        segment_id=seg_id,
                        category=item.get("category", "sentence_construction"),
                        original_text=orig,
                        corrected_text=item.get("corrected_text", orig),
                        explanation=item.get("explanation", "Grammar correction"),
                        rule_name=item.get("rule_name", "English Grammar Rule"),
                        suggested_alternative=item.get("suggested_alternative"),
                        severity=item.get("severity", "moderate"),
                        confidence=float(item.get("confidence", 0.90)),
                        evidence_status="verified",
                    )
                )

        except Exception as e:
            # Fall back to heuristic scoring if Gemini fails
            summary = f"Grammar analyzed via rule engine (AI inference fallback: {e})"

        # Calculate calibrated grammar score
        total_words = sum(s.word_count for s in segments)
        if total_words < 20:
            final_score = 85.0
        else:
            # Penalty per issue based on severity
            deductions = 0.0
            for f in findings:
                if f.severity == "major":
                    deductions += 6.0
                elif f.severity == "moderate":
                    deductions += 3.5
                else:
                    deductions += 1.5

            # Error rate per 100 words
            error_density = (len(findings) / max(1, total_words)) * 100
            heuristic_score = max(40.0, min(100.0, 100.0 - deductions - (error_density * 2.0)))
            # Blend heuristic with gemini score
            final_score = round(0.5 * heuristic_score + 0.5 * gemini_score, 1)

        return {
            "issues": findings,
            "score": final_score,
            "status": "available",
            "evidence_count": len(findings),
            "summary": summary,
        }

