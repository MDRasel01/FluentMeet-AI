"""
FluentMeet AI - Step 08: Personalized Recommendation Engine
Generates prioritized, actionable coaching suggestions linked directly to transcript evidence.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.analysis.modules.grammar import GrammarFinding
from app.analysis.modules.vocabulary import VocabularyInsightItem
from app.analysis.modules.fluency import FluencyMetricResult
from app.analysis.modules.sentence_structure import StructureObservation
from app.analysis.modules.speaking_patterns import RecurringPattern
from app.analysis.preprocessing.context import MeetingContext


@dataclass
class RecommendationItem:
    skill_category: str  # grammar, vocabulary, fluency, communication, contextual
    priority: str  # high, medium, low
    title: str
    actionable_suggestion: str
    evidence_reference: Optional[str]
    example: Optional[str]
    expected_outcome: Optional[str]


class RecommendationEngine:
    """
    Synthesizes findings across all linguistic modules into high-impact, prioritized coaching actions.
    """

    def generate_recommendations(
        self,
        grammar_findings: List[GrammarFinding],
        vocab_insights: List[VocabularyInsightItem],
        fluency_metrics: List[FluencyMetricResult],
        structure_observations: List[StructureObservation],
        recurring_patterns: List[RecurringPattern],
        context: MeetingContext,
    ) -> List[RecommendationItem]:
        """
        Synthesizes multi-module findings into prioritized recommendations.
        """
        recommendations: List[RecommendationItem] = []

        # 1. High Priority: Recurring Grammar Errors or Major Severity Errors
        major_grammar = [f for f in grammar_findings if f.severity == "major"]
        recurring_grammar = [p for p in recurring_patterns if p.pattern_type == "recurring_grammar_error"]

        if recurring_grammar:
            top_rec = recurring_grammar[0]
            recommendations.append(
                RecommendationItem(
                    skill_category="grammar",
                    priority="high",
                    title=f"Address {top_rec.description}",
                    actionable_suggestion=f"{top_rec.coaching_tip} Practice forming these structures correctly before your next meeting.",
                    evidence_reference=f"Observed in quotes: {', '.join(top_rec.examples[:2])}",
                    example=f"Example focus: Replace '{top_rec.examples[0]}' with the grammatically standard form.",
                    expected_outcome="Eliminates noticeable grammatical friction and increases executive authority.",
                )
            )
        elif major_grammar:
            mg = major_grammar[0]
            recommendations.append(
                RecommendationItem(
                    skill_category="grammar",
                    priority="high",
                    title=f"Refine {mg.rule_name}",
                    actionable_suggestion=mg.explanation,
                    evidence_reference=f"Segment {mg.segment_id}: '{mg.original_text}'",
                    example=f"Say: '{mg.corrected_text}' instead of '{mg.original_text}'",
                    expected_outcome="Strengthens structural accuracy and grammatical credibility.",
                )
            )

        # 2. High or Medium Priority: Fluency & Filler Words
        filler_metric = next((m for m in fluency_metrics if m.metric_name == "filler_word_rate"), None)
        if filler_metric and filler_metric.metric_value > 4.5:
            prio = "high" if filler_metric.metric_value > 7.0 else "medium"
            recommendations.append(
                RecommendationItem(
                    skill_category="fluency",
                    priority=prio,
                    title="Reduce Filler Word Frequency with Strategic Pauses",
                    actionable_suggestion=(
                        f"Your filler word rate is currently {filler_metric.metric_value}/minute. "
                        "When transitioning between ideas, replace verbal fillers ('um', 'like', 'basically') "
                        "with a silent 1-second pause. Pauses convey composure and give listeners time to absorb your points."
                    ),
                    evidence_reference=f"Recorded {filler_metric.evidence_count} filler words during the session.",
                    example="Instead of: 'So basically um we should do this' -> Try: '[Pause] We recommend proceeding with this approach.'",
                    expected_outcome="Projects higher executive presence, confidence, and deliberate speech pacing.",
                )
            )

        # 3. Speech Rate (WPM)
        wpm_metric = next((m for m in fluency_metrics if m.metric_name == "speech_rate_wpm"), None)
        if wpm_metric:
            if wpm_metric.metric_value < 105:
                recommendations.append(
                    RecommendationItem(
                        skill_category="fluency",
                        priority="medium",
                        title="Increase Speaking Momentum",
                        actionable_suggestion=(
                            f"Your speaking pace is {wpm_metric.metric_value} WPM, which is below the optimal "
                            "business meeting benchmark of 130-160 WPM. Rehearse key updates in advance to minimize hesitation."
                        ),
                        evidence_reference=f"Overall speaking rate: {wpm_metric.metric_value} WPM.",
                        example="Practice linking phrases fluently to maintain conversational momentum.",
                        expected_outcome="Keeps attendees engaged and delivers briefings with greater dynamism.",
                    )
                )
            elif wpm_metric.metric_value > 175:
                recommendations.append(
                    RecommendationItem(
                        skill_category="fluency",
                        priority="medium",
                        title="Modulate Speaking Pace for Multi-National Clarity",
                        actionable_suggestion=(
                            f"Your speaking pace is {wpm_metric.metric_value} WPM. Rapid delivery can reduce comprehension "
                            "in diverse international teams. Intentionally slow down when presenting technical specifications."
                        ),
                        evidence_reference=f"Overall speaking rate: {wpm_metric.metric_value} WPM.",
                        example="Articulate key terms distinctly and insert breath pauses after compound sentences.",
                        expected_outcome="Ensures cross-functional and non-native attendees follow complex arguments effortlessly.",
                    )
                )

        # 4. Vocabulary Enhancement & Professional Collocations
        if vocab_insights:
            v_item = vocab_insights[0]
            recommendations.append(
                RecommendationItem(
                    skill_category="vocabulary",
                    priority="medium",
                    title=f"Elevate Register with '{v_item.suggested_expression}'",
                    actionable_suggestion=v_item.explanation,
                    evidence_reference=f"Segment {v_item.segment_id}: '{v_item.original_expression}'",
                    example=v_item.example_sentence or f"Replace '{v_item.original_expression}' with '{v_item.suggested_expression}'.",
                    expected_outcome="Expands lexical versatility and fits the target professional communication context.",
                )
            )

        # 5. Sentence Structure & Run-Ons
        if structure_observations:
            obs = structure_observations[0]
            recommendations.append(
                RecommendationItem(
                    skill_category="sentence_structure",
                    priority="medium",
                    title="Restructure Complex Compound Sentences",
                    actionable_suggestion=obs.explanation,
                    evidence_reference=f"Segment {obs.segment_id}: '{obs.original_text}'",
                    example=obs.improved_text,
                    expected_outcome="Improves syntactic clarity and prevents rambling run-on clauses.",
                )
            )

        # 6. Sentence Starter Habit
        starter_pattern = next((p for p in recurring_patterns if p.pattern_type == "sentence_starter_habit"), None)
        if starter_pattern:
            recommendations.append(
                RecommendationItem(
                    skill_category="communication",
                    priority="low",
                    title="Diversify Sentence Starters",
                    actionable_suggestion=starter_pattern.coaching_tip,
                    evidence_reference=f"Detected pattern: {starter_pattern.description}",
                    example=f"Vary opening phrases rather than defaulting to '{starter_pattern.examples[0]}'",
                    expected_outcome="Adds variety and polish to verbal delivery.",
                )
            )

        # Priority sorting: High first, then Medium, then Low
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 3))

        return recommendations[:6]
