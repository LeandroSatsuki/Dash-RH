from __future__ import annotations

import importlib


def _reload_init_modules(monkeypatch, db_url: str, app_env: str, admin_password: str | None):
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("APP_ENV", app_env)
    monkeypatch.setenv("ADMIN_EMAIL", "admin@test.local")
    if admin_password is None:
        monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    else:
        monkeypatch.setenv("ADMIN_PASSWORD", admin_password)
    import src.db.database as database_module
    import src.db.models as models_module
    import src.db.init_db as init_db_module

    importlib.reload(database_module)
    importlib.reload(models_module)
    importlib.reload(init_db_module)
    return init_db_module


def test_development_aceita_fallback(monkeypatch, tmp_path):
    init_db_module = _reload_init_modules(monkeypatch, f"sqlite:///{tmp_path / 'dev.db'}", "development", None)
    init_db_module.init_db()


def test_production_sem_admin_password_falha(monkeypatch, tmp_path):
    init_db_module = _reload_init_modules(monkeypatch, f"sqlite:///{tmp_path / 'prod1.db'}", "production", None)
    try:
        init_db_module.init_db()
        assert False, "Era esperado erro"
    except RuntimeError as exc:
        assert "ADMIN_PASSWORD" in str(exc)


def test_production_com_senha_padrao_falha(monkeypatch, tmp_path):
    init_db_module = _reload_init_modules(monkeypatch, f"sqlite:///{tmp_path / 'prod2.db'}", "production", "Admin@123")
    try:
        init_db_module.init_db()
        assert False, "Era esperado erro"
    except RuntimeError as exc:
        assert "senha padrao" in str(exc)


def test_production_com_senha_forte_passa(monkeypatch, tmp_path):
    init_db_module = _reload_init_modules(monkeypatch, f"sqlite:///{tmp_path / 'prod3.db'}", "production", "SenhaForte@2026")
    init_db_module.init_db()


def test_production_sem_admin_email_falha(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'prod4.db'}")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("ADMIN_EMAIL", raising=False)
    monkeypatch.setenv("ADMIN_PASSWORD", "SenhaForte@2026")
    import src.db.database as database_module
    import src.db.models as models_module
    import src.db.init_db as init_db_module

    importlib.reload(database_module)
    importlib.reload(models_module)
    importlib.reload(init_db_module)
    try:
        init_db_module.init_db()
        assert False, "Era esperado erro"
    except RuntimeError as exc:
        assert "ADMIN_EMAIL" in str(exc)
