from src.services.external_notifications import dispatch_notification, send_email_notification, send_webhook_notification


def test_email_desativado_por_padrao(monkeypatch):
    monkeypatch.setenv("SMTP_ENABLED", "false")
    result = send_email_notification(to_email="x@test.local", subject="Teste", body="Body")
    assert result["status"] == "disabled"


def test_webhook_desativado_por_padrao(monkeypatch):
    monkeypatch.setenv("WEBHOOK_ENABLED", "false")
    result = send_webhook_notification(payload={"cpf": "12345678901"})
    assert result["status"] == "disabled"


def test_dispatch_interno_ok():
    result = dispatch_notification(channel="interno", payload={})
    assert result["status"] == "ok"
