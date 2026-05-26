from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///./data/app/dash_rh.db")


def ensure_database_path(database_url: str) -> None:
    if database_url.startswith("sqlite:///./"):
        relative_path = database_url.replace("sqlite:///./", "", 1)
        Path(relative_path).parent.mkdir(parents=True, exist_ok=True)
    elif database_url.startswith("sqlite:///"):
        absolute_path = database_url.replace("sqlite:///", "", 1)
        Path(absolute_path).parent.mkdir(parents=True, exist_ok=True)


DATABASE_URL = get_database_url()
ensure_database_path(DATABASE_URL)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
Base = declarative_base()
