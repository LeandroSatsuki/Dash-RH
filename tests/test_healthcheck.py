from __future__ import annotations

import importlib


def _load_api(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'health.db'}")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path / "backups"))
    import src.db.database as database_module
    import src.db.models as models_module
    import src.db.init_db as init_db_module
    import src.api.main as api_module

    importlib.reload(database_module)
    importlib.reload(models_module)
    importlib.reload(init_db_module)
    return importlib.reload(api_module)


def test_health_endpoint_retorna_payload(monkeypatch, tmp_path):
    api_module = _load_api(monkeypatch, tmp_path)
    payload = api_module.health()
    assert payload["app"] == "dash-rh-api"
    assert "database" in payload
    assert "migrations" in payload


def test_health_ready_endpoint(monkeypatch, tmp_path):
    api_module = _load_api(monkeypatch, tmp_path)
    api_module.init_db()
    data = api_module.build_ready_payload()
    assert data["status"] == "ready"
    assert data["database"] == "ok"
