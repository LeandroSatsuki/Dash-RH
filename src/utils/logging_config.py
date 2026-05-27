from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from src.services.masking import mask_cnpj, mask_cpf
from src.utils.config import get_settings


SENSITIVE_KEYS = {"password", "senha", "senha_hash", "secret_key", "token", "access_token", "smtp_password"}
MASKED_KEYS = {"cpf", "cnpj", "salario", "salario_base", "valor", "webhook_url", "database_url"}


def sanitize_log_payload(payload: Any, key: str | None = None) -> Any:
    normalized_key = (key or "").lower()
    if normalized_key in SENSITIVE_KEYS:
        return "[REDACTED]"
    if payload is None:
        return None
    if isinstance(payload, dict):
        return {str(item_key): sanitize_log_payload(item_value, str(item_key)) for item_key, item_value in payload.items()}
    if isinstance(payload, list):
        return [sanitize_log_payload(item) for item in payload]
    if normalized_key == "cpf":
        return mask_cpf(str(payload))
    if normalized_key == "cnpj":
        return mask_cnpj(str(payload))
    if normalized_key in MASKED_KEYS:
        return "[MASKED]"
    if isinstance(payload, str):
        if payload.startswith("http://") or payload.startswith("https://"):
            return payload.split("?", 1)[0]
        lowered = payload.lower()
        if "secret" in lowered or "token" in lowered or "password" in lowered:
            return "[REDACTED]"
        if payload.startswith("postgresql") or payload.startswith("sqlite"):
            return "[MASKED_URL]"
    return payload


def configure_logging(name: str = "dash_rh") -> logging.Logger:
    settings = get_settings(validate=False, ensure_dirs=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)

    if settings.log_to_file:
        logs_dir = Path("data/logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(logs_dir / f"{name}.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger


def log_structured(logger: logging.Logger, level: int, message: str, **payload: Any) -> None:
    sanitized = sanitize_log_payload(payload)
    logger.log(level, "%s | %s", message, json.dumps(sanitized, ensure_ascii=False, default=str))
