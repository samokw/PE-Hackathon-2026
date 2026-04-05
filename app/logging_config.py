"""Configure structlog for one JSON object per line (stdout)."""

import json
import logging
import os
import sys
import uuid
from typing import Any

import structlog

_log_file_fp = None


def _append_json_log_file(_logger: Any, _method_name: str, event_dict: dict) -> dict:
    """Duplicate each log event as JSON to LOG_FILE for Promtail/Loki (optional)."""
    global _log_file_fp
    if _log_file_fp is None:
        return event_dict
    try:
        line = json.dumps(event_dict, default=str, ensure_ascii=False) + "\n"
        _log_file_fp.write(line)
        _log_file_fp.flush()
    except OSError:
        pass
    return event_dict


def configure_logging(level: int = logging.INFO) -> None:
    """
    Idempotent-ish: safe to call once at app startup.
    Reduces duplicate access lines from Werkzeug; app events use JSON via structlog.

    Set LOG_FILE (e.g. /var/log/hackathon/app.log) to write the same JSON lines to a
    file for Promtail → Loki → Grafana on the server.
    """
    global _log_file_fp

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
        force=True,
    )

    log_path = os.environ.get("LOG_FILE", "").strip()
    if log_path:
        try:
            parent = os.path.dirname(log_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            _log_file_fp = open(log_path, "a", encoding="utf-8")
            sys.stderr.write(f"logging: also writing JSON logs to {log_path}\n")
        except OSError as exc:
            sys.stderr.write(f"logging: could not open LOG_FILE={log_path!r}: {exc}\n")
            _log_file_fp = None

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp")

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        _append_json_log_file,
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Plain Werkzeug access logs clash with our JSON lines; keep errors only.
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


def new_request_id() -> str:
    return str(uuid.uuid4())[:8]
