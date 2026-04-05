"""Configure structlog for one JSON object per line (stdout)."""

import logging
import sys
import uuid

import structlog


def configure_logging(level: int = logging.INFO) -> None:
    """
    Idempotent-ish: safe to call once at app startup.
    Reduces duplicate access lines from Werkzeug; app events use JSON via structlog.
    """
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
        force=True,
    )

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp")

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Plain Werkzeug access logs clash with our JSON lines; keep errors only.
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


def new_request_id() -> str:
    return str(uuid.uuid4())[:8]
