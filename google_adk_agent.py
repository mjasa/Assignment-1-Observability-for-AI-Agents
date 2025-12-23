"""
Example Google ADK (Gemini) agent instrumented with OpenTelemetry.
Assumes google-generativeai (Gemini) as the underlying ADK client.
"""
import logging
import os
import sys
import time
from typing import Any, Dict

from google import genai
from google.genai import types
from dotenv import load_dotenv

from observability import Observability

load_dotenv()

SERVICE_NAME = os.getenv("SERVICE_NAME_GOOGLE", "google-adk-agent")
obs = Observability(service_name=SERVICE_NAME)
logger = logging.getLogger(SERVICE_NAME)


def build_model():
    api_key = os.environ["GOOGLE_API_KEY"]
    model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")
    client = genai.Client(api_key=api_key)
    return client, model_name


def run(prompt: str) -> str:
    client, model_name = build_model()
    attributes: Dict[str, Any] = {"framework": "GoogleADK", "model": model_name}

    with obs.span("google_adk.run", attributes=attributes):
        obs.annotate_span("adk_start", {"prompt": prompt})
        attr_for_metrics = dict(attributes)
        tokens = None
        caught_exc: Exception | None = None
        response = None
        with obs.timed() as timer:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                success = True
            except Exception as exc:
                success = False
                caught_exc = exc
                error_attrs = {
                    "error.type": type(exc).__name__,
                    "error.message": str(exc),
                }
                attr_for_metrics.update(error_attrs)
                obs.annotate_span("adk_error", error_attrs)
        usage = getattr(response, "usage_metadata", None)
        if usage:
            prompt_tokens = getattr(usage, "prompt_token_count", 0) or 0
            completion_tokens = getattr(usage, "candidates_token_count", 0) or 0
            tokens = prompt_tokens + completion_tokens
            attr_for_metrics.update(
                {
                    "tokens.prompt": prompt_tokens,
                    "tokens.completion": completion_tokens,
                }
            )

        obs.record_run(
            latency_ms=timer.elapsed_ms,
            tokens=tokens,
            success=success,
            attributes=attr_for_metrics,
        )

        obs.annotate_span("adk_complete", {"latency_ms": timer.elapsed_ms})
        if success and response:
            logger.info("Google ADK result", extra={"result": response.text})
            return response.text
        raise caught_exc  # type: ignore[misc]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = os.getenv("PROMPT", "Explain observability for AI agents in 3 bullets.")
    try:
        print(run(prompt))
    finally:
        obs.shutdown()
