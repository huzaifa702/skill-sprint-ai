"""
SkillSprint AI - Google Gemini API Client & Controlled Retry Manager
Theme: OnboardVerse | Category: Generative AI PowerPlay

Handles authentication, timeouts, quota errors, network resilience,
and controlled retries without infinite loops or fabricated responses.
"""

import json
import logging
import os
import time
from typing import Any, Dict, Optional, Tuple
from src.core.config import DEFAULT_GEMINI_MODEL, GEMINI_API_KEY, GENAI_MAX_RETRIES, GENAI_REQUEST_TIMEOUT

logger = logging.getLogger("SkillSprintAI.GenAI")


class GenAIError(Exception):
    """Custom exception for Gemini API integration failures."""
    def __init__(self, message: str, status_code: int = 500, retry_count: int = 0):
        super().__init__(message)
        self.status_code = status_code
        self.retry_count = retry_count


def generate_structured_content(
    system_instruction: str,
    user_prompt: str,
    model_name: Optional[str] = None,
    temperature: float = 0.2
) -> Tuple[Dict[str, Any], int, int]:
    """
    Call Google Gemini API with system instructions, user prompt, and controlled retry logic.
    Returns (parsed_json_dict, latency_ms, retry_count).
    """
    model = model_name or DEFAULT_GEMINI_MODEL
    api_key = GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))

    if not api_key:
        raise GenAIError(
            "Gemini API key is not configured. Please set GEMINI_API_KEY in your environment or .env file.",
            status_code=401
        )

    last_error = None
    retries = 0

    for attempt in range(GENAI_MAX_RETRIES + 1):
        start_time = time.time()
        try:
            # Try official google-genai client
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                response_mime_type="application/json"
            )

            response = client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=config
            )

            latency_ms = int((time.time() - start_time) * 1000)
            raw_text = response.text.strip() if response.text else ""

            # Clean potential markdown fences if present
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

            parsed_json = json.loads(raw_text)
            return (parsed_json, latency_ms, retries)

        except ImportError:
            # Fallback to direct requests if SDK not yet available
            import urllib.request
            import urllib.error

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "system_instruction": {"parts": [{"text": system_instruction}]},
                "contents": [{"parts": [{"text": user_prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "responseMimeType": "application/json"
                }
            }
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})

            try:
                with urllib.request.urlopen(req, timeout=GENAI_REQUEST_TIMEOUT) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    latency_ms = int((time.time() - start_time) * 1000)
                    text_out = resp_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if text_out.startswith("```json"):
                        text_out = text_out[7:]
                    if text_out.endswith("```"):
                        text_out = text_out[:-3]
                    parsed_json = json.loads(text_out.strip())
                    return (parsed_json, latency_ms, retries)
            except Exception as http_err:
                last_error = http_err

        except Exception as e:
            last_error = e
            retries += 1
            logger.warning(f"GenAI call attempt {attempt+1} failed: {str(e)}. Retrying...")
            time.sleep(1.5 * (attempt + 1))

    error_msg = f"Generation service temporarily unavailable. Failed after {retries} retries: {str(last_error)}"
    logger.error(error_msg)
    raise GenAIError(error_msg, status_code=503, retry_count=retries)
