from datetime import datetime
from typing import Any

from bson import ObjectId


def serialize(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    return value


def public_user(user: dict[str, Any]) -> dict[str, Any]:
    safe = serialize(user)
    safe.pop("password_hash", None)
    return safe
