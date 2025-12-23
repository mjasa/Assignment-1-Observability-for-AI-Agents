# Observability for CrewAI + Google ADK Agents

This repo instruments both agent types with OpenTelemetry and ships telemetry to **Arize Phoenix** (chosen from the evaluated tools) via OTLP. The same pattern works for any OTLP-compatible backend.

## Tools Evaluated
- **CrewAI Observability (native):** built-in span logging for CrewAI only; no cross-framework or OTLP support.
- **Opik (Comet):** hosted + OSS UI for LLM traces/evals; Python-first; OTLP not first-class.
- **Langfuse:** OSS/hosted, strong trace UI and scoring; OTLP compatibility is limited/beta.
- **AgentOps.ai:** commercial, agent-centric analytics; closed-source and no OTLP.
- **Arize Phoenix:** OSS, OpenInference/OTLP-first, works with any Python agent, ships with trace UI.
- **OpenLIT:** OSS OTLP instrumentation helpers; relies on an external OTLP backend for UI/storage.

## Why Phoenix
- Open-source with local or hosted deployments; no vendor lock-in.
- **OTLP-first**: accepts traces/logs/metrics via standard OTLP over HTTP/gRPC.
- Framework-agnostic: works for CrewAI, Google ADK, or any custom agent because we emit OTel directly.
- UI for spans, token usage, and latency; compatible with Prom/Grafana for metrics export.
- Quick start via Docker or `phoenix serve` for local evidence capture.

## Architecture
```
CrewAI agent ----\
                   \--> OpenTelemetry SDK (traces, metrics, logs)
Google ADK agent --/            |
                                v
                         OTLP exporter
                                |
                        Arize Phoenix (collector + UI)
                                |
                         UI: http://localhost:6006
```

## Project Layout
```
.env.example          # Configuration for OTLP + model keys
observability.py      # Shared OTel setup + helper class
crew_agent.py         # CrewAI example with spans/metrics/logs
google_adk_agent.py   # Google ADK (Gemini) example with spans/metrics/logs
requirements.txt
OBSERVABILITY.md      # This document
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Start Phoenix (collector + UI)
docker run --rm -it -p 6006:6006 -p 4317:4317 -p 4318:4318 arizephoenix/phoenix:latest
# UI is at http://localhost:6006
# OTLP/HTTP (per container banner): http://localhost:6006/v1/{traces,metrics,logs}
# OTLP/gRPC: http://localhost:4317
```

## Running the agents (with telemetry)
```bash
# CrewAI
python crew_agent.py "Explain why observability matters for AI agents"

# Google ADK / Gemini
python google_adk_agent.py "Summarize observability best practices for agents"
```

After Phoenix starts, open the UI at http://localhost:6006 and click the **default** project card, then open **Spans** in the left nav to view traces.

Expected telemetry:
- **Traces:** spans `crew.run` and `google_adk.run` with events `*_start` and `*_complete`.
- **Metrics:** counters `agent_runs_total`, `agent_tokens_total`; histogram `agent_latency_ms`.
- **Logs:** structured events `agent_run_complete` and the agent results, all shipped over OTLP.

## Evidence to capture
1. Keep Phoenix UI open at http://localhost:6006.
2. Run each agent once; confirm new traces appear with service names `crewai-agent` and `google-adk-agent`.
3. Open a trace; verify span attributes (prompt, model, token counts) and events.
4. Show metrics panel (latency histogram, run count); if using Grafana, add Tempo/Loki/Prom panels pointing to the same OTLP collector.
5. Record a short screen video:
   - Terminal showing agent execution.
   - Phoenix UI showing incoming trace.
   - Drill into span details (events + attributes).
