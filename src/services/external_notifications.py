from __future__ import annotations

import os

from src.services.audit_service import sanitize_payload
from src.utils.logging_config import configure_logging, log_structured


logger = configure_logging("external_notifications")


def send_email_notification(*, to_email: str, subject: str, body: str) -> dict:
    if os.getenv("SMTP_ENABLED", "false").lower() != "true":
        log_structured(logger, 20, "email externo desativado", to_email=to_email, subject=subject)
        return {"status": "disabled", "channel": "email_smtp"}
    log_structured(logger, 30, "envio externo de email pulado", to_email=to_email, subject=subject)
    return {"status": "skipped", "channel": "email_smtp", "to": "[MASKED]"}


def send_webhook_notification(*, payload: dict) -> dict:
    if os.getenv("WEBHOOK_ENABLED", "false").lower() != "true":
        log_structured(logger, 20, "webhook externo desativado", payload=payload)
        return {"status": "disabled", "channel": "webhook"}
    log_structured(logger, 30, "envio externo de webhook pulado", payload=payload)
    return {"status": "skipped", "channel": "webhook", "payload": sanitize_payload(payload)}


def dispatch_notification(*, channel: str, payload: dict) -> dict:
    if channel == "interno":
        return {"status": "ok", "channel": "interno"}
    if channel == "email_smtp":
        return send_email_notification(to_email=payload.get("to_email", ""), subject=payload.get("subject", ""), body=payload.get("body", ""))
    if channel == "webhook":
        return send_webhook_notification(payload=payload)
    raise ValueError("Canal de notificacao invalido.")
