import os

import structlog
from flask import jsonify, request
from peewee import DatabaseProxy, Model, PostgresqlDatabase

db = DatabaseProxy()
log = structlog.get_logger(__name__)


class BaseModel(Model):
    class Meta:
        database = db


def init_db(app):
    database = PostgresqlDatabase(
        os.environ.get("DATABASE_NAME", "hackathon_db"),
        host=os.environ.get("DATABASE_HOST", "localhost"),
        port=int(os.environ.get("DATABASE_PORT", 5432)),
        user=os.environ.get("DATABASE_USER", "postgres"),
        password=os.environ.get("DATABASE_PASSWORD", "postgres"),
    )
    db.initialize(database)

    log.info(
        "database_configured",
        host=os.environ.get("DATABASE_HOST", "localhost"),
        port=int(os.environ.get("DATABASE_PORT", 5432)),
        database=os.environ.get("DATABASE_NAME", "hackathon_db"),
        component="database",
    )

    @app.before_request
    def _db_connect():
        # Metrics do not need PostgreSQL; allow scraping when DB is unavailable.
        if request.path == "/metrics":
            return None
        try:
            db.connect(reuse_if_open=True)
        except Exception as e:
            log.error(
                "database_connection_failed",
                error=str(e),
                component="database",
                exc_info=True,
            )
            return jsonify({"error": "Service unavailable"}), 503

    @app.teardown_appcontext
    def _db_close(exc):
        if not db.is_closed():
            db.close()
