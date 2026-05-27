from __future__ import annotations

import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.db.database import engine
from src.utils.config import ConfigError, get_settings
from src.utils.logging_config import configure_logging, log_structured


logger = configure_logging("migrate")


def run_migrations() -> None:
    settings = get_settings(validate=True, ensure_dirs=True)
    if not settings.database_url:
        raise ConfigError("DATABASE_URL ausente. Configure o banco antes de rodar migracoes.")
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    log_structured(logger, 20, "inicio migracao", app_env=settings.app_env)
    inspector = inspect(engine)
    if not inspector.has_table("alembic_version"):
        existing_tables = [table_name for table_name in inspector.get_table_names() if table_name != "alembic_version"]
        if existing_tables:
            log_structured(logger, 30, "schema existente sem alembic_version detectado, aplicando stamp", tables=existing_tables[:10])
            command.stamp(config, "head")
    try:
        command.upgrade(config, "head")
    except OperationalError as exc:
        if settings.database_url.startswith("sqlite") and "already exists" in str(exc).lower():
            log_structured(logger, 30, "upgrade inicial encontrou schema existente, aplicando stamp", error=str(exc))
            command.stamp(config, "head")
        else:
            raise
    log_structured(logger, 20, "fim migracao", app_env=settings.app_env)


def main() -> None:
    run_migrations()


if __name__ == "__main__":
    main()
