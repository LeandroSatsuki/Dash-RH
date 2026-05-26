from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import UTC, datetime, timedelta


def get_secret_key() -> str:
    return os.getenv("SECRET_KEY", "change-me")


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 310000)
    return f"{salt}${base64.b64encode(digest).decode('utf-8')}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, digest = password_hash.split("$", 1)
    except ValueError:
        return False
    expected = hash_password(password, salt)
    return hmac.compare_digest(expected, password_hash)


def create_access_token(payload: dict, expires_minutes: int = 480) -> str:
    data = payload.copy()
    data["exp"] = int((datetime.now(UTC) + timedelta(minutes=expires_minutes)).timestamp())
    raw = json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(get_secret_key().encode("utf-8"), raw, hashlib.sha256).hexdigest()
    return f"{base64.urlsafe_b64encode(raw).decode('utf-8')}.{signature}"


def decode_access_token(token: str) -> dict | None:
    try:
        encoded, signature = token.split(".", 1)
        raw = base64.urlsafe_b64decode(encoded.encode("utf-8"))
        expected = hmac.new(get_secret_key().encode("utf-8"), raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        data = json.loads(raw.decode("utf-8"))
        if data.get("exp", 0) < int(datetime.now(UTC).timestamp()):
            return None
        return data
    except Exception:
        return None
