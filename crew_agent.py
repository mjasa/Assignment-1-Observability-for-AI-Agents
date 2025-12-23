"""
Example CrewAI agent with OpenTelemetry instrumentation sending data to Arize Phoenix.
"""
import logging
import os
import sys
import time
from typing import Any, Dict

from dotenv import load_dotenv

# IMPORTANT: Load environment and set up observability BEFORE importing CrewAI
# because CrewAI initializes its own tracer provider
load_dotenv()

from observability import Observability

SERVICE_NAME = os.getenv("SERVICE_NAME_CREW", "crewai-agent")
obs = Observability(service_name=SERVICE_NAME)
logger = logging.getLogger(SERVICE_NAME)

# Now import CrewAI after observability is configured
from crewai import Agent, Crew, Task
from langchain_openai import ChatOpenAI


def build_crew() -> Crew:
    """Constructs a simple single-agent crew."""
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    researcher = Agent(
        role="Researcher",
        goal="Explain concepts concisely",
        backstory="Senior engineer who teaches clearly.",
        llm=llm,
        verbose=True,
    )
    task = Task(
        description="Answer the user question: {topic}",
        expected_output="A short, precise answer with 2-3 bullet points.",
        agent=researcher,
    )
    return Crew(agents=[researcher], tasks=[task])


def run(prompt: str) -> str:
    crew = build_crew()
    attributes: Dict[str, Any] = {"framework": "CrewAI", "input.prompt": prompt}

    with obs.span("crew.run", attributes=attributes):
        obs.annotate_span("crew_start", {"prompt": prompt})
        tokens = None
        attr_for_metrics = dict(attributes)
        with obs.timed() as timer:
            caught_exc: Exception | None = None
            try:
                result = crew.kickoff(inputs={"topic": prompt})
                tokens = getattr(result, "token_usage", None)
                success = True
            except Exception as exc:
                success = False
                caught_exc = exc
                error_attrs = {
                    "error.type": type(exc).__name__,
                    "error.message": str(exc),
                }
                attr_for_metrics.update(error_attrs)
                obs.annotate_span("crew_error", error_attrs)
        obs.record_run(
            latency_ms=timer.elapsed_ms,
            tokens=tokens if isinstance(tokens, int) else None,
            success=success,
            attributes=attr_for_metrics,
        )
        obs.annotate_span("crew_complete", {"latency_ms": timer.elapsed_ms})
        if success:
            logger.info("CrewAI result", extra={"result": str(result)})
            return str(result)
        if caught_exc:
            raise caught_exc


if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = os.getenv("PROMPT", "Why is observability critical for AI agents?")
    try:
        print(run(prompt))
    finally:
        obs.shutdown()
