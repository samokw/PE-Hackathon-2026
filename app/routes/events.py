import json
from datetime import datetime

from flask import Blueprint, jsonify, request

from app.models.events import UrlEvent
from app.models.urls import Url
from app.models.users import User
from app.routes.helpers import event_to_dict

events_bp = Blueprint("events", __name__)


def _validate_event_create(data):
    if data is None or not isinstance(data, dict):
        return {"_": "expected JSON object"}
    errors = {}
    if "url_id" not in data:
        errors["url_id"] = "required"
    elif type(data["url_id"]) is not int:
        errors["url_id"] = "must be an integer"
    if "user_id" not in data:
        errors["user_id"] = "required"
    elif type(data["user_id"]) is not int:
        errors["user_id"] = "must be an integer"
    if "event_type" not in data:
        errors["event_type"] = "required"
    elif not isinstance(data["event_type"], str):
        errors["event_type"] = "must be a string"
    if "details" not in data:
        errors["details"] = "required"
    elif not isinstance(data["details"], dict):
        errors["details"] = "must be an object"
    return errors if errors else None


@events_bp.route("/events", methods=["GET"])
def events_list():
    query = UrlEvent.select().order_by(UrlEvent.id)
    return jsonify([event_to_dict(event) for event in query])


@events_bp.route("/events", methods=["POST"])
def events_create():
    data = request.get_json(silent=True)
    err = _validate_event_create(data)
    if err:
        return jsonify(err), 400

    url = Url.get_or_none(Url.id == data["url_id"])
    if url is None:
        return jsonify({"url_id": "url does not exist"}), 404

    user = User.get_or_none(User.id == data["user_id"])
    if user is None:
        return jsonify({"user_id": "user does not exist"}), 404

    now = datetime.utcnow()
    event = UrlEvent.create(
        url=url,
        user=user,
        event_type=data["event_type"],
        timestamp=now,
        details=json.dumps(data["details"]),
    )

    return jsonify(event_to_dict(event)), 201
