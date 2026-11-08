# Step 08 — Google Gemini API Integration Specification

## 1. Provider & Model Architecture
- **Primary AI Provider**: Google Gemini REST API.
- **Model**: `gemini-1.5-flash` (or `gemini-2.0-flash`).
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}`.
- **Protocol**: Direct async HTTP via `httpx.AsyncClient`.

## 2. Structured JSON Enforcement
All prompts leverage Gemini's native `response_mime_type="application/json"` and strict JSON schemas:
```json
{
  "system_instruction": {
    "parts": [{"text": "SYSTEM_INSTRUCTION"}]
  },
  "contents": [
    {"role": "user", "parts": [{"text": "USER_PROMPT"}]}
  ],
  "generationConfig": {
    "temperature": 0.2,
    "responseMimeType": "application/json"
  }
}
```

## 3. Resiliency & Rate Limit Handling
- **Exponential Backoff**: Automatic retry handling for HTTP 429 (Rate Limit) and HTTP 500/502/503/504 errors up to 3 retries.
- **Timeout Handling**: Configurable 30.0s request timeout.
- **Deterministic Mock Fallback**: When `GEMINI_API_KEY` is omitted or in test environments, deterministic local mock responses are provided to ensure zero pipeline crashes and full offline testability.
