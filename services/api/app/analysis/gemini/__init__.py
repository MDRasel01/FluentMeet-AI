"""
FluentMeet AI - Step 08: Gemini Module Package
"""
from app.analysis.gemini.client import GeminiClient, GeminiAPIError, GeminiRateLimitError
from app.analysis.gemini.prompts import (
    SYSTEM_INSTRUCTION,
    GRAMMAR_PROMPT_TEMPLATE,
    VOCABULARY_PROMPT_TEMPLATE,
    SENTENCE_STRUCTURE_PROMPT_TEMPLATE,
    COMMUNICATION_PROMPT_TEMPLATE,
)

__all__ = [
    "GeminiClient",
    "GeminiAPIError",
    "GeminiRateLimitError",
    "SYSTEM_INSTRUCTION",
    "GRAMMAR_PROMPT_TEMPLATE",
    "VOCABULARY_PROMPT_TEMPLATE",
    "SENTENCE_STRUCTURE_PROMPT_TEMPLATE",
    "COMMUNICATION_PROMPT_TEMPLATE",
]
