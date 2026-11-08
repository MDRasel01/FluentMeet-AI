"""
FluentMeet AI - Step 08: Speaking Pattern Intelligence Module
Detects recurring habits, crutch phrases, and persistent error patterns across speaker turns.
"""

import re
from typing import List, Dict, Any
from collections import Counter
from dataclasses import dataclass

from app.analysis.preprocessing.cleaner import CleanedSegment
from app.analysis.modules.grammar import GrammarFinding
from app.analysis.modules.vocabulary import VocabularyInsightItem


@dataclass
class RecurringPattern:
    pattern_type: str  # recurring_grammar_error, crutch_phrase, sentence_starter_habit, filler_frequency
    description: str
    frequency: int
    examples: List[str]
    coaching_tip: str


class SpeakingPatternAnalyzer:
    """
    Synthesizes multi-turn speaking patterns across grammar, vocabulary, and sentence initiation.
    """

    def analyze(
        self,
        segments: List[CleanedSegment],
        grammar_findings: List[GrammarFinding],
        vocab_insights: List[VocabularyInsightItem],
    ) -> List[RecurringPattern]:
        """
        Extracts recurring communication habits.
        """
        patterns: List[RecurringPattern] = []

        # 1. Check for recurring grammar error categories (>= 2 occurrences of same category)
        cat_counts = Counter(f.category for f in grammar_findings)
        for cat, count in cat_counts.items():
            if count >= 2:
                examples = [f.original_text for f in grammar_findings if f.category == cat][:3]
                patterns.append(
                    RecurringPattern(
                        pattern_type="recurring_grammar_error",
                        description=f"Recurring {cat.replace('_', ' ')} errors observed {count} times.",
                        frequency=count,
                        examples=examples,
                        coaching_tip=f"Focus on {cat.replace('_', ' ')} consistency during spontaneous speech.",
                    )
                )

        # 2. Check for sentence starter habits (e.g., repeatedly starting utterances with 'so', 'basically', 'actually', 'and')
        starters: List[str] = []
        starter_map: Dict[str, List[str]] = {}
        for seg in segments:
            words = seg.cleaned_text.split()
            if words:
                first_word = words[0].lower().strip(",.")
                if first_word in ("so", "basically", "actually", "and", "well", "like", "i", "yeah"):
                    starters.append(first_word)
                    starter_map.setdefault(first_word, []).append(seg.cleaned_text[:60] + "...")

        starter_counts = Counter(starters)
        for word, count in starter_counts.items():
            if count >= 3 and len(segments) >= 5:
                patterns.append(
                    RecurringPattern(
                        pattern_type="sentence_starter_habit",
                        description=f"Repetitively initiates utterances with '{word.capitalize()}' ({count} times).",
                        frequency=count,
                        examples=starter_map[word][:3],
                        coaching_tip=f"Try varying your opening transitions (e.g., 'To begin with', 'Regarding that point', 'Directly speaking').",
                    )
                )

        # 3. Check for recurring vocabulary overuses
        vocab_type_counts = Counter(v.original_expression.lower() for v in vocab_insights)
        for expr, count in vocab_type_counts.items():
            if count >= 2:
                patterns.append(
                    RecurringPattern(
                        pattern_type="crutch_phrase",
                        description=f"Overuse of conversational phrase '{expr}' ({count} times).",
                        frequency=count,
                        examples=[expr],
                        coaching_tip=f"Substitute with domain-specific professional alternatives to diversify expression.",
                    )
                )

        return patterns

