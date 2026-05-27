from __future__ import annotations

from pathlib import Path

import pytest

from scripts import backup_postgres, restore_postgres


def test_backup_sqlite_copia_arquivo(monkeypatch, tmp_path):
    db_file = tmp_path / "app.db"
    db_file.write_text("sqlite-data", encoding="utf-8")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path / "backups"))
    target = backup_postgres.run_backup()
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "sqlite-data"


def test_restore_exige_confirm(monkeypatch, tmp_path):
    backup_file = tmp_path / "restore.sqlite3"
    backup_file.write_text("content", encoding="utf-8")
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'app.db'}")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path / "backups"))
    with pytest.raises(RuntimeError):
        restore_postgres.restore_backup(backup_file=backup_file, confirm=False)


def test_restore_sqlite_copia_arquivo(monkeypatch, tmp_path):
    backup_file = tmp_path / "restore.sqlite3"
    backup_file.write_text("restored", encoding="utf-8")
    database_path = tmp_path / "db" / "app.db"
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path / "backups"))
    destination = restore_postgres.restore_backup(backup_file=backup_file, confirm=True)
    assert Path(destination).exists()
    assert Path(destination).read_text(encoding="utf-8") == "restored"
