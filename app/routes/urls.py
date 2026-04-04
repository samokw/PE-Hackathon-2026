import secrets
import string
from datetime import datetime

from flask import Blueprint, jsonify, redirect, request

from app.models.events import UrlEvent
from app.models.urls import Url
from app.models.users import User
from app.routes.helpers import url_to_dict

urls_bp = Blueprint("urls", __name__)

_ALPHABET = string.ascii_letters + string.digits


def _generate_short_code(length: int = 6) -> str:
    for _ in range(128):
        code = "".join(secrets.choice(_ALPHABET) for _ in range(length))
        if not Url.select().where(Url.short_code == code).exists():
            return code
    raise RuntimeError("unable to generate unique short_code")


def _parse_is_active_param(raw):
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if s == "true":
        return True
    if s == "false":
        return False
    return None


def _validate_url_create(data):
    if data is None or not isinstance(data, dict):
        return {"_": "expected JSON object"}
    errors = {}
    if "user_id" not in data:
        errors["user_id"] = "required"
    elif type(data["user_id"]) is not int:
        errors["user_id"] = "must be an integer"
    if "original_url" not in data:
        errors["original_url"] = "required"
    elif not isinstance(data["original_url"], str):
        errors["original_url"] = "must be a string"
    elif not data["original_url"].strip():
        errors["original_url"] = "must not be empty"
    if "title" not in data:
        errors["title"] = "required"
    elif not isinstance(data["title"], str):
        errors["title"] = "must be a string"
    return errors if errors else None


@urls_bp.route("/urls", methods=["POST"])
def urls_create():
    data = request.get_json(silent=True)
    err = _validate_url_create(data)
    if err:
        return jsonify(err), 400

    user = User.get_or_none(User.id == data["user_id"])
    if user is None:
        return jsonify({"user_id": "user does not exist"}), 404

    now = datetime.utcnow()
    short_code = _generate_short_code()
    url = Url.create(
        user=user,
        short_code=short_code,
        original_url=data["original_url"].strip(),
        title=data["title"],
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    return jsonify(url_to_dict(url)), 201


@urls_bp.route("/urls", methods=["GET"])
def urls_list():
    urls_query = Url.select().order_by(Url.id)
    filter_user_id = request.args.get("user_id", type=int)
    if filter_user_id is not None:
        urls_query = urls_query.where(Url.user_id == filter_user_id)
    active_filter = _parse_is_active_param(request.args.get("is_active"))
    if active_filter is not None:
        urls_query = urls_query.where(Url.is_active == active_filter)
    return jsonify([url_to_dict(url_record) for url_record in urls_query])


@urls_bp.route("/urls/<string:short_code>/redirect", methods=["GET"])
def urls_redirect(short_code):
    url_record = Url.get_or_none(Url.short_code == short_code)
    if url_record is None or not url_record.is_active:
        return jsonify(error="URL not found"), 404
    return redirect(url_record.original_url, code=302)


@urls_bp.route("/urls/<int:url_id>", methods=["GET"])
def urls_get(url_id):
    url_record = Url.get_or_none(Url.id == url_id)
    if url_record is None:
        return jsonify(error="URL not found"), 404
    return jsonify(url_to_dict(url_record))


@urls_bp.route("/urls/<int:url_id>", methods=["PUT"])
def urls_update(url_id):
    url_record = Url.get_or_none(Url.id == url_id)
    if url_record is None:
        return jsonify(error="URL not found"), 404

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"_": "expected JSON object"}), 400

    if "title" in data:
        if not isinstance(data["title"], str):
            return jsonify({"title": "must be a string"}), 400
        url_record.title = data["title"]
    if "is_active" in data:
        if not isinstance(data["is_active"], bool):
            return jsonify({"is_active": "must be a boolean"}), 400
        url_record.is_active = data["is_active"]

    url_record.updated_at = datetime.utcnow()
    url_record.save()
    return jsonify(url_to_dict(url_record))


@urls_bp.route("/urls/<int:url_id>", methods=["DELETE"])
def urls_delete(url_id):
    url_record = Url.get_or_none(Url.id == url_id)
    if url_record is None:
        return jsonify(error="URL not found"), 404

    UrlEvent.delete().where(UrlEvent.url_id == url_id).execute()
    Url.delete().where(Url.id == url_id).execute()

    return "", 204
