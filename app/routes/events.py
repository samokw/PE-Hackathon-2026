from flask import Blueprint, jsonify

from app.models.events import UrlEvent
from app.routes.helpers import event_to_dict

events_bp = Blueprint("events", __name__)


@events_bp.route("/events", methods=["GET"])
def events_list():
    query = UrlEvent.select().order_by(UrlEvent.id)
    return jsonify([event_to_dict(event) for event in query])
