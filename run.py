import structlog

from app import create_app
from app.database import db
from app.models.events import UrlEvent
from app.models.urls import Url
from app.models.users import User

log = structlog.get_logger(__name__)

app = create_app()

with app.app_context():
    db.create_tables([User, Url, UrlEvent], safe=True)
    log.info(
        "database_tables_ready",
        models=["User", "Url", "UrlEvent"],
        component="run",
    )

if __name__ == "__main__":
    log.info(
        "dev_server_starting",
        host="127.0.0.1",
        port=5000,
        debug=True,
        component="run",
    )
    app.run(host="0.0.0.0", port=5000, debug=True)
