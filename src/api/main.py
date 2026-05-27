from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import FastAPI, HTTPException
from sqlalchemy import inspect, text

from src.api.routes import (
    admissoes,
    afastamentos,
    alertas,
    auth,
    banco_horas,
    beneficios,
    cargos,
    centros_custo,
    colaboradores,
    departamentos,
    desligamentos,
    documentos,
    documentos_obrigatorios,
    ferias,
    folha,
    indicadores,
    jornadas,
    notificacoes,
    ponto,
    sst,
    tarefas,
    workflows,
)
from src.db.database import engine
from src.db.init_db import init_db
from src.utils.config import get_settings, validate_runtime_settings
from src.utils.logging_config import configure_logging, log_structured


logger = configure_logging("api")
ROOT = Path(__file__).resolve().parents[2]


def _database_status() -> str:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return "ok"


def _migrations_status() -> str:
    inspector = inspect(engine)
    if not inspector.has_table("alembic_version"):
        return "pending"
    config = Config(str(ROOT / "alembic.ini"))
    script_dir = ScriptDirectory.from_config(config)
    expected_heads = set(script_dir.get_heads())
    with engine.connect() as connection:
        current_rows = connection.execute(text("SELECT version_num FROM alembic_version")).fetchall()
    current_heads = {row[0] for row in current_rows}
    return "ok" if current_heads == expected_heads else "pending"


def build_health_payload() -> dict:
    settings = get_settings(validate=False)
    database = "ok"
    migrations = "unknown"
    try:
        database = _database_status()
        migrations = _migrations_status()
    except Exception:
        database = "error"
        migrations = "error"
    return {
        "status": "ok" if database == "ok" else "degraded",
        "app": "dash-rh-api",
        "ambiente": settings.app_env,
        "database": database,
        "migrations": migrations,
        "timestamp": datetime.now(UTC).isoformat(),
    }


def build_ready_payload() -> dict:
    settings = validate_runtime_settings()
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    inspector = inspect(engine)
    required_tables = ["usuarios", "colaboradores", "auditoria"]
    missing_tables = [table_name for table_name in required_tables if not inspector.has_table(table_name)]
    if missing_tables:
        raise RuntimeError(f"Tabelas obrigatorias ausentes: {', '.join(missing_tables)}")
    if not settings.upload_dir.exists() or not settings.upload_dir.is_dir():
        raise RuntimeError("UPLOAD_DIR inacessivel.")
    return {
        "status": "ready",
        "app": "dash-rh-api",
        "ambiente": settings.app_env,
        "database": "ok",
        "migrations": _migrations_status(),
        "timestamp": datetime.now(UTC).isoformat(),
    }


@asynccontextmanager
async def lifespan(_: FastAPI):
    validate_runtime_settings()
    init_db()
    log_structured(logger, 20, "api iniciada", app="dash-rh-api", ambiente=get_settings(validate=False).app_env)
    yield


app = FastAPI(title="Dash-RH Operacional API", version="1.0.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(departamentos.router)
app.include_router(cargos.router)
app.include_router(centros_custo.router)
app.include_router(colaboradores.router)
app.include_router(admissoes.router)
app.include_router(beneficios.router)
app.include_router(ferias.router)
app.include_router(afastamentos.router)
app.include_router(folha.router)
app.include_router(desligamentos.router)
app.include_router(documentos.router)
app.include_router(jornadas.router)
app.include_router(ponto.router)
app.include_router(banco_horas.router)
app.include_router(documentos_obrigatorios.router)
app.include_router(sst.router)
app.include_router(alertas.router)
app.include_router(workflows.router)
app.include_router(tarefas.router)
app.include_router(notificacoes.router)
app.include_router(indicadores.router)


@app.get("/health")
def health():
    return build_health_payload()


@app.get("/health/ready")
def health_ready():
    try:
        return build_ready_payload()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
