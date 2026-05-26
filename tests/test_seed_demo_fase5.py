from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scripts import seed_demo
from src.db.database import Base
from src.db.models import Notificacao, Tarefa, WorkflowInstancia


def test_seed_demo_fase5_cria_workflows_tarefas_e_notificacoes(monkeypatch, tmp_path):
    engine = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(seed_demo, "SessionLocal", TestingSession)
    monkeypatch.setattr(seed_demo, "init_db", lambda: None)
    result = seed_demo.seed_demo()
    with TestingSession() as db:
        assert len(db.query(Tarefa).all()) > 0
        assert len(db.query(Notificacao).all()) > 0
        assert len(db.query(WorkflowInstancia).all()) > 0
    assert result["tarefas"] > 0
