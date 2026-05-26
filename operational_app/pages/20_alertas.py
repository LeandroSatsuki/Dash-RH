from __future__ import annotations

import pandas as pd
import streamlit as st

from operational_app.common import db_session, safe_run
from src.services import alerts


def render(user: dict):
    st.subheader("Alertas Operacionais")
    col1, col2 = st.columns(2)
    if col1.button("Gerar alertas"):
        safe_run(lambda: _gerar(user), success_message="Alertas atualizados.")
    severidade = col2.selectbox("Severidade", ["Todos", "critica", "alta", "media", "baixa"])
    with db_session() as db:
        itens = alerts.listar_alertas(db, severidade=None if severidade == "Todos" else severidade)
    st.dataframe(pd.DataFrame([{"id": item.id, "tipo": item.tipo, "severidade": item.severidade, "titulo": item.titulo, "status": item.status, "entidade_tipo": item.entidade_tipo, "entidade_id": item.entidade_id} for item in itens]), use_container_width=True)
    if itens:
        alerta_id = st.selectbox("Alerta para acao", [item.id for item in itens])
        justificativa = st.text_input("Justificativa", value="Tratado operacionalmente.")
        col1, col2 = st.columns(2)
        if col1.button("Resolver alerta"):
            safe_run(lambda: _resolver(user, alerta_id, justificativa), success_message="Alerta resolvido.")
        if col2.button("Ignorar alerta"):
            safe_run(lambda: _ignorar(user, alerta_id, justificativa), success_message="Alerta ignorado.")


def _gerar(user):
    with db_session() as db:
        alerts.gerar_alertas(db)


def _resolver(user, alerta_id, justificativa):
    with db_session() as db:
        alerts.resolver_alerta(db, alerta_id, user["id"], justificativa)


def _ignorar(user, alerta_id, justificativa):
    with db_session() as db:
        alerts.ignorar_alerta(db, alerta_id, user["id"], justificativa)
