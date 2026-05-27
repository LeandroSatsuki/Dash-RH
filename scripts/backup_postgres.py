from __future__ import annotations

import shutil
import subprocess
import sys
import os
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.config import get_settings
from src.utils.logging_config import configure_logging, log_structured


logger = configure_logging("backup")


def build_backup_path(settings, suffix: str) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    settings.backup_dir.mkdir(parents=True, exist_ok=True)
    return settings.backup_dir / f"dash_rh_{timestamp}.{suffix}"


def run_backup() -> Path:
    settings = get_settings(validate=True, ensure_dirs=True)
    database_url = settings.database_url
    log_structured(logger, 20, "inicio backup", app_env=settings.app_env, database_url=database_url)
    if database_url.startswith("sqlite"):
        source = Path(database_url.replace("sqlite:///", "", 1).replace("./", "", 1))
        if not source.exists():
            raise RuntimeError("Arquivo SQLite nao encontrado para backup.")
        target = build_backup_path(settings, "sqlite3")
        shutil.copy2(source, target)
        log_structured(logger, 20, "backup sqlite concluido", arquivo=str(target))
        return target

    url = make_url(database_url)
    target = build_backup_path(settings, "dump")
    env = dict(**os.environ)
    if url.password:
        env["PGPASSWORD"] = url.password
    command = [
        "pg_dump",
        "--format=custom",
        "--file",
        str(target),
        "--host",
        url.host or "localhost",
        "--port",
        str(url.port or 5432),
        "--username",
        url.username or "",
        "--dbname",
        url.database or "",
    ]
    subprocess.run(command, check=True, env=env)
    log_structured(logger, 20, "backup postgres concluido", arquivo=str(target))
    return target


def main() -> None:
    target = run_backup()
    print(target)


if __name__ == "__main__":
    main()
