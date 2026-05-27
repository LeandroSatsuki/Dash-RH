from __future__ import annotations

import pytest
from sqlalchemy.exc import OperationalError

from scripts import migrate
from src.utils.config import ConfigError


def test_migrate_script_roda_upgrade(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'app.db'}")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path / "backups"))
    called = {}

    def fake_upgrade(config, revision):
        called["revision"] = revision

    monkeypatch.setattr(migrate.command, "upgrade", fake_upgrade)
    migrate.run_migrations()
    assert called["revision"] == "head"


def test_migrate_script_aplica_stamp_em_schema_existente(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'app.db'}")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path / "backups"))
    called = {"stamp": 0, "upgrade": 0}

    class FakeInspector:
        def has_table(self, name):
            return False

        def get_table_names(self):
            return ["usuarios"]

    monkeypatch.setattr(migrate, "inspect", lambda engine: FakeInspector())
    monkeypatch.setattr(migrate.command, "stamp", lambda config, revision: called.__setitem__("stamp", called["stamp"] + 1))
    monkeypatch.setattr(migrate.command, "upgrade", lambda config, revision: called.__setitem__("upgrade", called["upgrade"] + 1))
    migrate.run_migrations()
    assert called["stamp"] == 1
    assert called["upgrade"] == 1


def test_migrate_script_recupera_de_tabela_existente(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'app.db'}")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path / "backups"))
    called = {"stamp": 0}

    def fake_upgrade(config, revision):
        raise OperationalError("create table", {}, Exception("already exists"))

    monkeypatch.setattr(migrate.command, "upgrade", fake_upgrade)
    monkeypatch.setattr(migrate.command, "stamp", lambda config, revision: called.__setitem__("stamp", called["stamp"] + 1))
    migrate.run_migrations()
    assert called["stamp"] == 1


def test_migrate_script_falha_sem_database_url(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("SECRET_KEY", "secret-key-super-forte")
    monkeypatch.setenv("ADMIN_EMAIL", "admin@test.local")
    monkeypatch.setenv("ADMIN_PASSWORD", "SenhaForte@2026")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path / "backups"))
    with pytest.raises(ConfigError):
        migrate.run_migrations()
