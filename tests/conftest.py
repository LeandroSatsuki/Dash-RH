from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.db.database import Base
from src.db import models as _models  # noqa: F401
from src.db.models import Usuario
from src.auth.security import hash_password


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    admin = Usuario(nome="Admin", email="admin@test.local", senha_hash=hash_password("123456"), perfil="admin", ativo=True)
    session.add(admin)
    session.commit()
    session.refresh(admin)
    try:
        yield session
    finally:
        session.close()
