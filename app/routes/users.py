import csv
import os
import tempfile
from datetime import datetime

from flask import Blueprint, jsonify, request

from app.models.events import UrlEvent
from app.models.urls import Url
from app.models.users import User
from app.routes.helpers import user_to_dict
from app.seed import load_csv

users_bp = Blueprint("users", __name__)


def _error_dict(payload: dict, status=400):
    return jsonify(payload), status


@users_bp.route("/users/bulk", methods=["POST"])
def users_bulk():
    uploaded_file = request.files.get("file")
    if uploaded_file is None or uploaded_file.filename == "":
        return _error_dict({"file": "missing multipart file field"})

    raw = uploaded_file.read()
    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", suffix=".csv", delete=False
    ) as temp_file:
        temp_file.write(text)
        path = temp_file.name
    try:
        with open(path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
        count = len(rows)
        load_csv(path)
    except ValueError as exc:
        return _error_dict({"csv": str(exc)})
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass

    return jsonify(count=count), 201


@users_bp.route("/users", methods=["GET"])
def users_list():
    users_query = User.select().order_by(User.id)
    if "page" in request.args or "per_page" in request.args:
        page = request.args.get("page", default=1, type=int) or 1
        per_page = request.args.get("per_page", default=20, type=int) or 20
        if page < 1 or per_page < 1:
            return _error_dict({"page": "must be positive integers"})
        page_items = list(users_query.paginate(page, per_page))
        return jsonify(users=[user_to_dict(user) for user in page_items])
    return jsonify([user_to_dict(user) for user in users_query])


@users_bp.route("/users/<int:user_id>", methods=["GET"])
def users_get(user_id):
    user = User.get_or_none(User.id == user_id)
    if user is None:
        return jsonify(error="User not found"), 404
    return jsonify(user_to_dict(user))


def _validate_create_payload(data):
    errors = {}
    if data is None:
        return {"_": "expected JSON object"}
    if not isinstance(data, dict):
        return {"_": "expected JSON object"}
    if "username" not in data:
        errors["username"] = "required"
    elif not isinstance(data["username"], str):
        errors["username"] = "must be a string"
    if "email" not in data:
        errors["email"] = "required"
    elif not isinstance(data["email"], str):
        errors["email"] = "must be a string"
    if errors:
        return errors
    return None


@users_bp.route("/users", methods=["POST"])
def users_create():
    data = request.get_json(silent=True)
    err = _validate_create_payload(data)
    if err:
        return jsonify(err), 400

    now = datetime.utcnow()
    user = User.create(username=data["username"], email=data["email"], created_at=now)
    return jsonify(user_to_dict(user)), 201


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
def users_update(user_id):
    user = User.get_or_none(User.id == user_id)
    if user is None:
        return jsonify(error="User not found"), 404

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"_": "expected JSON object"}), 400

    if "username" not in data:
        return jsonify({"username": "required"}), 400
    if not isinstance(data["username"], str):
        return jsonify({"username": "must be a string"}), 400

    user.username = data["username"]
    user.save()
    return jsonify(user_to_dict(user))


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
def users_delete(user_id):
    user = User.get_or_none(User.id == user_id)
    if user is None:
        return jsonify(error="User not found"), 404

    user_url_ids = Url.select(Url.id).where(Url.user_id == user_id)
    UrlEvent.delete().where(
        (UrlEvent.user_id == user_id) | (UrlEvent.url_id.in_(user_url_ids))
    ).execute()
    Url.delete().where(Url.user_id == user_id).execute()
    User.delete().where(User.id == user_id).execute()

    return "", 204
