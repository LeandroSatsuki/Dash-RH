from __future__ import annotations

import os


def get_app_env() -> str:
    return os.getenv("APP_ENV", "development").strip().lower() or "development"


def is_development() -> bool:
    return get_app_env() == "development"


def is_production() -> bool:
    return get_app_env() == "production"


def get_upload_dir() -> str:
    return os.getenv("UPLOAD_DIR", "data/uploads")
