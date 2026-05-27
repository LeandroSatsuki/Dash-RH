from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.config import get_settings
from src.utils.logging_config import configure_logging, log_structured


logger = configure_logging("restore")


def restore_backup(*, backup_file: str | Path, confirm: bool) -> Path:
    if not confirm:
        raise RuntimeError("Restore bloqueado. Use --confirm para confirmar a operacao.")
    settings = get_settings(validate=True, ensure_dirs=True)
    target_file = Path(backup_file)
    if not target_file.exists():
        raise RuntimeError("Arquivo de backup nao encontrado.")

    log_structured(logger, 20, "inicio restore", arquivo=str(target_file), app_env=settings.app_env)
    database_url = settings.database_url
    if database_url.startswith("sqlite"):
        destination = Path(database_url.replace("sqlite:///", "", 1).replace("./", "", 1))
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target_file, destination)
        log_structured(logger, 20, "restore sqlite concluido", destino=str(destination))
        return destination

    url = make_url(database_url)
    env = dict(**os.environ)
    if url.password:
        env["PGPASSWORD"] = url.password
    command = [
        "pg_restore",
        "--clean",
        "--if-exists",
        "--no-owner",
        "--host",
        url.host or "localhost",
        "--port",
        str(url.port or 5432),
        "--username",
        url.username or "",
        "--dbname",
        url.database or "",
        str(target_file),
    ]
    subprocess.run(command, check=True, env=env)
    log_structured(logger, 20, "restore postgres concluido", arquivo=str(target_file))
    return target_file


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args(argv)
    restore_backup(backup_file=args.file, confirm=args.confirm)


if __name__ == "__main__":
    main()
