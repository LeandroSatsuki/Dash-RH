from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.utils.config import get_database_url


def is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite")


def ensure_database_path(database_url: str) -> None:
    if database_url.startswith("sqlite:///./"):
        relative_path = database_url.replace("sqlite:///./", "", 1)
        Path(relative_path).parent.mkdir(parents=True, exist_ok=True)
    elif database_url.startswith("sqlite:///"):
        absolute_path = database_url.replace("sqlite:///", "", 1)
        Path(absolute_path).parent.mkdir(parents=True, exist_ok=True)


DATABASE_URL = get_database_url()
ensure_database_path(DATABASE_URL)

connect_args = {"check_same_thread": False} if is_sqlite_url(DATABASE_URL) else {}
engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
Base = declarative_base()
