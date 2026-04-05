import time

import structlog
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request

from app.database import init_db
from app.logging_config import configure_logging, new_request_id
from app.metrics import (
    http_errors_total,
    http_request_duration_seconds,
    http_requests_total,
    metrics_response,
)
from app.routes import register_routes

log = structlog.get_logger("app")


def create_app():
    load_dotenv()

    configure_logging()

    app = Flask(__name__)

    @app.before_request
    def _bind_request_context():
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=new_request_id(),
            component="http",
        )
        g._request_started = time.perf_counter()
        g._metrics_error_recorded = False

    @app.after_request
    def _log_request(response):
        duration_ms = None
        if hasattr(g, "_request_started"):
            duration_ms = round((time.perf_counter() - g._request_started) * 1000, 2)
        log.info(
            "http_request",
            method=request.method,
            path=request.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )

        if request.path != "/metrics":
            endpoint = request.endpoint or "unknown"
            if hasattr(g, "_request_started"):
                http_request_duration_seconds.labels(
                    method=request.method,
                    endpoint=endpoint,
                ).observe(time.perf_counter() - g._request_started)
            http_requests_total.labels(
                method=request.method,
                endpoint=endpoint,
                status=str(response.status_code),
            ).inc()
            if response.status_code >= 500:
                http_errors_total.labels(endpoint=endpoint, kind="5xx").inc()
                g._metrics_error_recorded = True

        return response

    @app.teardown_request
    def _log_request_error(exc):
        if exc is not None:
            log.error(
                "http_request_error",
                method=request.method,
                path=request.path,
                error=str(exc),
                exc_type=type(exc).__name__,
                exc_info=True,
            )
            if request.path != "/metrics" and not getattr(
                g, "_metrics_error_recorded", False
            ):
                http_errors_total.labels(
                    endpoint=request.endpoint or "unknown",
                    kind="exception",
                ).inc()

    init_db(app)

    from app import models  # noqa: F401 - registers models with Peewee

    register_routes(app)

    log.info("application_ready", component="app")

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    @app.route("/metrics")
    def metrics():
        return metrics_response()

    return app
