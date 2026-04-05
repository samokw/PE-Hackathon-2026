"""Prometheus metrics (text format at GET /metrics)."""

from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest, REGISTRY

# Custom application counters (process CPU/RAM come from default REGISTRY collectors where available)
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests handled",
    ("method", "endpoint", "status"),
)

http_errors_total = Counter(
    "http_errors_total",
    "HTTP 5xx responses and unhandled request exceptions",
    ("endpoint", "kind"),
)


def metrics_response():
    """Prometheus text exposition format."""
    from flask import Response

    return Response(generate_latest(REGISTRY), mimetype=CONTENT_TYPE_LATEST)
