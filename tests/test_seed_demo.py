from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from scripts import seed_demo
from src.db.database import Base
from src.db.models import Colaborador, Empresa


def test_seed_demo_bloqueado_em_producao(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    try:
        seed_demo.ensure_not_production()
        assert False, "Era esperado bloqueio"
    except RuntimeError as exc:
        assert "bloqueado" in str(exc)


def test_seed_demo_cria_dados(monkeypatch, tmp_path):
    engine = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(seed_demo, "SessionLocal", TestingSession)
    monkeypatch.setattr(seed_demo, "init_db", lambda: None)
    result = seed_demo.seed_demo()
    with TestingSession() as db:
        assert db.scalar(select(Empresa).limit(1)) is not None
        total_colaboradores = db.scalar(select(Colaborador).count()) if False else len(db.scalars(select(Colaborador)).all())
        assert total_colaboradores >= 30
    assert result["colaboradores"] >= 30
