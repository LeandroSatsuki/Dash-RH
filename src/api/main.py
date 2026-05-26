from __future__ import annotations

from fastapi import FastAPI

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
    ponto,
    sst,
    tarefas,
    notificacoes,
    workflows,
)
from src.db.init_db import init_db

init_db()

app = FastAPI(title="Dash-RH Operacional API", version="1.0.0")

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
    return {"status": "ok"}
