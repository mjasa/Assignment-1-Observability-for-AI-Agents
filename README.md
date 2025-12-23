# Observability for AI Agents

This project demonstrates how to implement comprehensive observability for AI agents using OpenTelemetry and Arize Phoenix. It includes examples for both CrewAI and Google ADK (Gemini) agents with full tracing, metrics, and logging capabilities.

## Features

- 🔍 **OpenTelemetry Integration**: Complete OTLP instrumentation for traces, metrics, and logs
- 🤖 **Multiple Agent Frameworks**: Examples for CrewAI and Google Gemini agents
- 📊 **Arize Phoenix Support**: Send telemetry data to Arize Phoenix for analysis
- 🛠️ **Reusable Observability Module**: Shared observability configuration across different agents
- 📝 **Comprehensive Logging**: Structured logging with OpenTelemetry context

## Project Structure

```
.
├── crew_agent.py          # CrewAI agent example with observability
├── google_adk_agent.py    # Google ADK (Gemini) agent example
├── observability.py       # Shared observability configuration module
├── requirements.txt       # Python dependencies
├── OBSERVABILITY.md       # Detailed observability documentation
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
python crew_agent.py
```

This agent uses CrewAI to create a research agent that can answer questions with full observability tracking.

### Running the Google ADK Agent

```bash
python google_adk_agent.py
```

This agent uses Google's Gemini model to generate responses with OpenTelemetry instrumentation.

## Setting Up Arize Phoenix (Optional)

To visualize your telemetry data:

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

### Agent Examples

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
