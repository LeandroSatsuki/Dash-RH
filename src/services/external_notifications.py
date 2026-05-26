from __future__ import annotations

import os

from src.services.audit_service import sanitize_payload


def send_email_notification(*, to_email: str, subject: str, body: str) -> dict:
    if os.getenv("SMTP_ENABLED", "false").lower() != "true":
        return {"status": "disabled", "channel": "email_smtp"}
    return {"status": "skipped", "channel": "email_smtp", "to": "[MASKED]"}


def send_webhook_notification(*, payload: dict) -> dict:
    if os.getenv("WEBHOOK_ENABLED", "false").lower() != "true":
        return {"status": "disabled", "channel": "webhook"}
    return {"status": "skipped", "channel": "webhook", "payload": sanitize_payload(payload)}


def dispatch_notification(*, channel: str, payload: dict) -> dict:
    if channel == "interno":
        return {"status": "ok", "channel": "interno"}
    if channel == "email_smtp":
        return send_email_notification(to_email=payload.get("to_email", ""), subject=payload.get("subject", ""), body=payload.get("body", ""))
    if channel == "webhook":
        return send_webhook_notification(payload=payload)
    raise ValueError("Canal de notificacao invalido.")
