import time

import structlog
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request

from app.database import init_db
from app.logging_config import configure_logging, new_request_id
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

    init_db(app)

    from app import models  # noqa: F401 - registers models with Peewee

    register_routes(app)

    log.info("application_ready", component="app")

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    return app
