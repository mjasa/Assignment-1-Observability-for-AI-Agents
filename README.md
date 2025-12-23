# Observability for AI Agents

This project demonstrates how to implement comprehensive observability for AI agents using OpenTelemetry and Arize Phoenix. It instruments both CrewAI and Google ADK agents with OpenTelemetry and ships telemetry to **Arize Phoenix** via OTLP. The same pattern works for any OTLP-compatible backend.

## Features

- 🔍 **OpenTelemetry Integration**: Complete OTLP instrumentation for traces, metrics, and logs
- 🤖 **Multiple Agent Frameworks**: Examples for CrewAI and Google Gemini agents
- 📊 **Arize Phoenix Support**: Send telemetry data to Arize Phoenix for analysis
- 🛠️ **Reusable Observability Module**: Shared observability configuration across different agents
- 📝 **Comprehensive Logging**: Structured logging with OpenTelemetry context
- 🏗️ **Framework-Agnostic**: OTLP-first approach works with any Python agent

## Tools Evaluated

Before selecting Arize Phoenix, the following observability tools were evaluated:

- **CrewAI Observability (native):** Built-in span logging for CrewAI only; no cross-framework or OTLP support.
- **Opik (Comet):** Hosted + OSS UI for LLM traces/evals; Python-first; OTLP not first-class.
- **Langfuse:** OSS/hosted, strong trace UI and scoring; OTLP compatibility is limited/beta.
- **AgentOps.ai:** Commercial, agent-centric analytics; closed-source and no OTLP.
- **Arize Phoenix:** OSS, OpenInference/OTLP-first, works with any Python agent, ships with trace UI.
- **OpenLIT:** OSS OTLP instrumentation helpers; relies on an external OTLP backend for UI/storage.

### Why Phoenix?

- **Open-source** with local or hosted deployments; no vendor lock-in.
- **OTLP-first**: Accepts traces/logs/metrics via standard OTLP over HTTP/gRPC.
- **Framework-agnostic**: Works for CrewAI, Google ADK, or any custom agent because we emit OTel directly.
- **Rich UI** for spans, token usage, and latency; compatible with Prom/Grafana for metrics export.
- **Quick start** via Docker or `phoenix serve` for local evidence capture.

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

## Project Structure

```
.
├── crew_agent.py          # CrewAI agent example with observability
├── google_adk_agent.py    # Google ADK (Gemini) agent example
├── observability.py       # Shared observability configuration module
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (for CrewAI agent)
- Google API key (for Google ADK agent)
- Arize Phoenix (optional, for telemetry visualization)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd "Assignment 1 Observability for AI Agents"
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Google Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-1.5-pro

# Service Names (optional)
SERVICE_NAME_CREW=crewai-agent
SERVICE_NAME_GOOGLE=google-adk-agent

# OTLP Configuration (optional)
OTLP_ENDPOINT=http://127.0.0.1:6006/v1/traces
OTLP_HEADERS=
```

## Usage

### Running the CrewAI Agent

```bash
python crew_agent.py "Explain why observability matters for AI agents"
```

This agent uses CrewAI to create a research agent that can answer questions with full observability tracking.

### Running the Google ADK Agent

```bash
python google_adk_agent.py "Summarize observability best practices for agents"
```

This agent uses Google's Gemini model to generate responses with OpenTelemetry instrumentation.

### Expected Telemetry

After running the agents, open Phoenix UI at http://localhost:6006 and click the **default** project card, then open **Spans** to view traces. You should see:

- **Traces:** Spans `crew.run` and `google_adk.run` with events `*_start` and `*_complete`
- **Metrics:** Counters `agent_runs_total`, `agent_tokens_total`; histogram `agent_latency_ms`
- **Logs:** Structured events `agent_run_complete` and agent results, all shipped over OTLP
- **Service Names:** `crewai-agent` and `google-adk-agent` appear as separate services
- **Span Attributes:** Prompt, model, token counts visible in span details
## Setting Up Arize Phoenix (Optional)


To visualize your telemetry data, you need to start Phoenix as a collector and UI:

### Option 1: Using Docker (Recommended)

```bash
docker run --rm -it -p 6006:6006 -p 4317:4317 -p 4318:4318 arizephoenix/phoenix:latest
```

This exposes:
- UI at `http://localhost:6006`
- OTLP/HTTP at `http://localhost:6006/v1/{traces,metrics,logs}`
- OTLP/gRPC at `http://localhost:4317`
1. Install Arize Phoenix:
```bash
pip install arize-phoenix
```

2. Start Phoenix in a separate terminal:
```bash
python -m phoenix.server.main serve
```

3. Open your browser to `http://localhost:6006` to view traces and metrics

## Observability Features

The `observability.py` module provides:

- **Tracing**: Track agent execution flow and LLM calls
- **Metrics**: Monitor agent performance and resource usage
- **Logging**: Structured logs with trace context
- **OTLP Export**: Send data to Phoenix or other OTLP-compatible backends

For detailed information about the observability implementation, see [OBSERVABILITY.md](OBSERVABILITY.md).

## Key Components

### Observability Module

The `Observability` class in `observability.py` handles:
- TracerProvider configuration
- MetricProvider setup
- LoggerProvider initialization
- OTLP exporter configuration
- Resource attributes

###Evidence Capture Checklist

To validate the observability implementation:

1. Keep Phoenix UI open at http://localhost:6006
2. Run each agent once; confirm new traces appear with service names `crewai-agent` and `google-adk-agent`
3. Open a trace; verify span attributes (prompt, model, token counts) and events
4. Show metrics panel (latency histogram, run count); if using Grafana, add Tempo/Loki/Prom panels pointing to the same OTLP collector
5. Optional: Record a screen video showing:
   - Terminal with agent execution
   - Phoenix UI showing incoming traces
   - Drill into span details (events + attributes)

##  Agent Examples

Both agent examples demonstrate:
- Proper initialization order (observability before agent frameworks)
- Manual span creation for custom operations
- Metric recording (operation counts, durations, token usage)
- Structured logging with trace context

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required for CrewAI |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o-mini` |
| `GOOGLE_API_KEY` | Google API key | Required for Google ADK |
| `GOOGLE_MODEL` | Google model name | `gemini-1.5-pro` |
| `SERVICE_NAME_CREW` | Service name for CrewAI | `crewai-agent` |
| `SERVICE_NAME_GOOGLE` | Service name for Google ADK | `google-adk-agent` |
| `OTLP_ENDPOINT` | OTLP endpoint URL | `http://127.0.0.1:6006/v1/traces` |
| `OTLP_HEADERS` | OTLP headers | Empty |

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is provided as-is for educational purposes.

## Learn More

- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
- [Arize Phoenix](https://docs.arize.com/phoenix)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Google Generative AI](https://ai.google.dev/)
