from __future__ import annotations

from src.utils.logging_config import sanitize_log_payload


def test_logging_sanitiza_campos_sensiveis():
    payload = {
        "cpf": "12345678901",
        "secret_key": "segredo",
        "salary": 1000,
        "database_url": "postgresql+psycopg://user:pass@localhost:5432/db",
        "nested": {"webhook_url": "https://secret.local/hook?token=abc"},
    }
    sanitized = sanitize_log_payload(payload)
    assert sanitized["cpf"] != "12345678901"
    assert sanitized["secret_key"] == "[REDACTED]"
    assert sanitized["database_url"] == "[MASKED]"
    assert sanitized["nested"]["webhook_url"] == "[MASKED]"


def test_logging_sanitiza_strings_de_url():
    assert sanitize_log_payload("https://example.local/path?token=abc") == "https://example.local/path"
