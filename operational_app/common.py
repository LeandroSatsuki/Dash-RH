from __future__ import annotations

from contextlib import contextmanager

from src.db.init_db import init_db
from src.db.session import SessionLocal


init_db()


@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
