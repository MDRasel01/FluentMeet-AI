"""
FluentMeet AI - Step 08: Direct Async Gemini REST API Client
Communicates with Google Gemini API using httpx with exponential backoff,
structured JSON response parsing, and anti-prompt-injection sanitization.
"""

import asyncio
import json
import logging
import re
from typing import Dict, Any, Optional, List
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiAPIError(Exception):
    """Base exception for Gemini API failures."""
    pass


class GeminiRateLimitError(GeminiAPIError):
    """Raised when receiving HTTP 429 Too Many Requests."""
    pass


class GeminiClient:
    """
    Async client for Google Gemini 1.5 / 2.0 Flash REST API.
    Enforces strict JSON output, automatic retry backoff, and input sanitization.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        self.api_key = api_key or getattr(settings, "GEMINI_API_KEY", "")
        self.model = model or getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
        self.timeout_seconds = timeout_seconds or float(getattr(settings, "GEMINI_TIMEOUT_SECONDS", 30))
        self.max_retries = max_retries or int(getattr(settings, "GEMINI_MAX_RETRIES", 3))

    @staticmethod
    def sanitize_untrusted_text(text: str) -> str:
        """
        Neutralizes prompt-injection attempts inside transcript text.
        Strips XML boundary exploits, system override keywords, and control tokens.
        """
        if not text:
            return ""

        # Break XML tag closures that could escape the enclosure
        text = text.replace("</untrusted_transcript>", "&lt;/untrusted_transcript&gt;")
        text = text.replace("<untrusted_transcript>", "&lt;untrusted_transcript&gt;")
        text = text.replace("```json", "'''json").replace("```", "'''")

        # Neutralize common prompt-injection commands
        patterns = [
            r"(?i)ignore\s+(all\s+)?previous\s+instructions",
            r"(?i)system\s*:\s*",
            r"(?i)developer\s*mode",
            r"(?i)you\s+are\s+now\s+a",
        ]
        for pattern in patterns:
            text = re.sub(pattern, "[FILTERED_COMMAND]", text)

        return text

    @staticmethod
    def format_segments_for_prompt(segments: List[Any]) -> str:
        """
        Formats transcript segments with their IDs and timestamps for grounded analysis.
        """
        lines = []
        for s in segments:
            seg_id = getattr(s, "segment_id", getattr(s, "id", "unknown"))
            start = getattr(s, "start_time_ms", 0)
            end = getattr(s, "end_time_ms", 0)
            text = getattr(s, "cleaned_text", getattr(s, "text", ""))
            safe_text = GeminiClient.sanitize_untrusted_text(text)
            lines.append(f"[SEGMENT id='{seg_id}' time='{start}-{end}ms']: \"{safe_text}\"")
        return "\n".join(lines)

    async def generate_json(
        self,
        system_instruction: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Executes a prompt against Gemini REST API expecting a structured JSON response.
        Applies exponential backoff for transient errors.
        """
        # If API key is dummy/mock, return mock responses for safe unit testing
        if not self.api_key or self.api_key in ("mock-key", "test", "your_gemini_api_key_here"):
            return self._mock_fallback(user_prompt)

        url = f"{self.BASE_URL}/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json"
            }
        }

        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.post(url, json=payload)

                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get("candidates", [])
                        if not candidates:
                            raise GeminiAPIError("Gemini returned empty candidates")

                        parts = candidates[0].get("content", {}).get("parts", [])
                        if not parts:
                            raise GeminiAPIError("Gemini candidate has no content parts")

                        raw_text = parts[0].get("text", "{}")
                        return self._parse_json_response(raw_text)

                    elif response.status_code == 429:
                        wait = (2 ** attempt) * 1.5
                        logger.warning(f"Gemini 429 Rate Limit hit. Backing off for {wait:.1f}s (Attempt {attempt+1}/{self.max_retries})")
                        await asyncio.sleep(wait)
                        continue

                    elif response.status_code in (500, 502, 503, 504):
                        wait = (2 ** attempt) * 1.0
                        logger.warning(f"Gemini Server Error {response.status_code}. Backing off for {wait:.1f}s")
                        await asyncio.sleep(wait)
                        continue

                    else:
                        raise GeminiAPIError(f"Gemini API Error {response.status_code}: {response.text}")

            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_exception = exc
                if attempt < self.max_retries:
                    wait = (2 ** attempt) * 1.0
                    logger.warning(f"Gemini connection timeout/network error: {exc}. Retrying in {wait:.1f}s...")
                    await asyncio.sleep(wait)
                else:
                    raise GeminiAPIError(f"Gemini request failed after {self.max_retries} retries: {exc}") from exc

        raise GeminiAPIError(f"Exhausted retries: {last_exception}")

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """
        Parses JSON from Gemini output, stripping any residual markdown wrapper if present.
        """
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from Gemini output: {text[:200]}")
            raise GeminiAPIError(f"Invalid JSON returned by Gemini: {e}")

    def _mock_fallback(self, prompt: str) -> Dict[str, Any]:
        """
        Generates realistic structured mock data for unit tests and local runs without API keys.
        """
        # Extract segment IDs if available in prompt
        segment_ids = re.findall(r"id=['\"]([^'\"]+)['\"]", prompt)
        sample_id = segment_ids[0] if segment_ids else "mock-segment-001"

        if "grammatical accuracy" in prompt.lower():
            return {
                "issues": [
                    {
                        "segment_id": sample_id,
                        "category": "tense",
                        "original_text": "we was discussing",
                        "corrected_text": "we were discussing",
                        "explanation": "Subject-verb agreement: the plural subject 'we' takes 'were', not 'was'.",
                        "rule_name": "Subject-Verb Agreement (Plural Past Continuous)",
                        "suggested_alternative": "we were reviewing",
                        "severity": "moderate",
                        "confidence": 0.95,
                    }
                ],
                "grammar_score": 88.0,
                "summary": "Good overall grammar with minor subject-verb agreement slip.",
            }

        elif "vocabulary" in prompt.lower():
            return {
                "insights": [
                    {
                        "segment_id": sample_id,
                        "insight_type": "word_choice",
                        "original_expression": "good things",
                        "suggested_expression": "favorable outcomes",
                        "explanation": "Using more precise terminology elevates executive presence.",
                        "example_sentence": "The strategy yielded favorable outcomes for our quarterly targets.",
                        "confidence": 0.92,
                    }
                ],
                "vocabulary_score": 84.0,
                "summary": "Clear vocabulary with opportunities for more precise professional collocations.",
            }

        elif "sentence structure" in prompt.lower():
            return {
                "observations": [
                    {
                        "segment_id": sample_id,
                        "issue_type": "run_on",
                        "original_text": "and then we went there and we did that",
                        "improved_text": "Next, we proceeded with the deployment and completed the verification.",
                        "explanation": "Break excessive coordinate clauses with 'and' into distinct complete sentences.",
                        "severity": "minor",
                        "confidence": 0.90,
                    }
                ],
                "structure_score": 86.0,
                "summary": "Balanced sentence variety with occasional conversational run-on clauses.",
            }

        elif "communicative effectiveness" in prompt.lower():
            return {
                "insights": [
                    {
                        "insight_type": "response_relevance",
                        "title": "Clear Technical Explanation",
                        "description": "Provided direct and relevant responses to questions asked during the discussion.",
                        "evidence": "Direct answers to architectural inquiries.",
                        "confidence": 0.92,
                    }
                ],
                "communication_score": 90.0,
                "summary": "Effective communicator with strong active listening markers.",
            }

        return {"status": "ok", "summary": "Default mock analysis completed."}

