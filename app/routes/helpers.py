import json
from datetime import datetime


def format_dt(dt):
    if dt is None:
        return None
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    return str(dt)


def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": format_dt(user.created_at),
    }


def url_to_dict(url):
    return {
        "id": url.id,
        "user_id": url.user_id,
        "short_code": url.short_code,
        "original_url": url.original_url,
        "title": url.title,
        "is_active": url.is_active,
        "created_at": format_dt(url.created_at),
        "updated_at": format_dt(url.updated_at),
    }


def event_to_dict(event):
    details = event.details
    if isinstance(details, str):
        try:
            details = json.loads(details)
        except json.JSONDecodeError:
            details = {}
    elif details is None:
        details = {}
    if not isinstance(details, dict):
        details = {}
    return {
        "id": event.id,
        "url_id": event.url_id,
        "user_id": event.user_id,
        "event_type": event.event_type,
        "timestamp": format_dt(event.timestamp),
        "details": details,
    }
