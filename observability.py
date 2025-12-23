"""
OpenTelemetry-based observability bootstrap shared by CrewAI and Google ADK agents.

This module configures tracing, metrics, and logs using OTLP exporters so telemetry
can flow into Arize Phoenix (or any other OTLP-compatible backend).
"""
import logging
import os
import time
import uuid
from typing import Any, Dict, Optional

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry._logs import set_logger_provider


def _parse_headers(raw: str) -> Dict[str, str]:
    """Parses OTLP headers from env string like 'key=value,foo=bar'."""
    headers: Dict[str, str] = {}
    if not raw:
        return headers
    for pair in raw.split(","):
        if "=" in pair:
            key, value = pair.split("=", 1)
            headers[key.strip()] = value.strip()
    return headers


def setup_observability(service_name: str) -> None:
    """
    Configure global OpenTelemetry providers for traces, metrics, and logs.
    Call once at process start before importing other modules that emit telemetry.
    """
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:6006").rstrip("/")
    headers = _parse_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS", ""))
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.instance.id": os.getenv("SERVICE_INSTANCE_ID", str(uuid.uuid4())),
        }
    )

    # --- Traces ---
    trace_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(trace_provider)
    span_exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces", headers=headers)
    trace_provider.add_span_processor(BatchSpanProcessor(span_exporter))

    # --- Metrics ---
    # Phoenix OTLP/HTTP endpoint only supports traces, not metrics
    # metric_reader = PeriodicExportingMetricReader(
    #     OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics", headers=headers)
    # )
    # meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    # metrics.set_meter_provider(meter_provider)

    # --- Logs ---
    # Phoenix OTLP/HTTP endpoint only supports traces, not logs
    # logger_provider = LoggerProvider(resource=resource)
    # set_logger_provider(logger_provider)
    # log_exporter = OTLPLogExporter(endpoint=f"{endpoint}/v1/logs", headers=headers)
    # logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    # Setup local console logging for developer visibility
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    )
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(console_handler)


class Observability:
    """
    Lightweight helper for recording agent spans, metrics, and logs.
    Metrics are intentionally minimal: run count, latency, and token usage.
    """

    def __init__(self, service_name: str):
        setup_observability(service_name)
        self.service_name = service_name
        self.tracer = trace.get_tracer(service_name)
        self.logger = logging.getLogger(service_name)
        self.trace_provider = trace.get_tracer_provider()

        # Metrics disabled - Phoenix OTLP/HTTP doesn't support them
        # self.meter = metrics.get_meter(service_name)
        # self.meter_provider = metrics.get_meter_provider()
        # self.run_counter = self.meter.create_counter(
        #     "agent_runs_total", description="Count of agent invocations"
        # )
        # self.latency_hist = self.meter.create_histogram(
        #     "agent_latency_ms", description="End-to-end latency (ms)"
        # )
        # self.token_counter = self.meter.create_counter(
        #     "agent_tokens_total", description="Total tokens consumed"
        # )

    def span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Returns a context manager span with optional attributes."""
        return self.tracer.start_as_current_span(name, attributes=attributes or {})

    def record_run(
        self,
        latency_ms: float,
        tokens: Optional[int],
        success: bool,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        attrs = attributes or {}
        attrs.update({"success": success})
        # Metrics disabled - Phoenix OTLP/HTTP doesn't support them
        # self.run_counter.add(1, attributes=attrs)
        # self.latency_hist.record(latency_ms, attributes=attrs)
        # if tokens is not None:
        #     self.token_counter.add(tokens, attributes=attrs)
        self.logger.info(
            "agent_run_complete",
            extra={"latency_ms": latency_ms, "tokens": tokens, **attrs},
        )

    def annotate_span(self, message: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        span = trace.get_current_span()
        if span and span.is_recording():
            span.add_event(message, attributes=attributes or {})
        self.logger.info(message, extra=attributes or {})

    def timed(self):
        """Context manager yielding a timer; returns elapsed ms on exit."""
        class _Timer:
            def __enter__(self_inner):
                self_inner.start = time.perf_counter()
                return self_inner

            def __exit__(self_inner, exc_type, exc, tb):
                self_inner.elapsed_ms = (time.perf_counter() - self_inner.start) * 1000
                return False

        return _Timer()

    def shutdown(self) -> None:
        """
        Flush all pending telemetry and shutdown providers.
        Call this before process exit to ensure all spans/metrics/logs are exported.
        """
        # Force flush traces
        if hasattr(self.trace_provider, "force_flush"):
            self.trace_provider.force_flush()
