from __future__ import annotations

import pandas as pd
import streamlit as st

from operational_app.common import db_session, safe_run
from src.crud import notificacoes as crud_notificacoes
from src.services import notification_service


def render(user: dict):
    st.subheader("Notificacoes")
    with db_session() as db:
        notificacoes = crud_notificacoes.listar(db, usuario_id=user["id"])
    st.dataframe(pd.DataFrame([{"id": item.id, "titulo": item.titulo, "tipo": item.tipo, "severidade": item.severidade, "lida": item.lida, "criado_em": item.criado_em} for item in notificacoes]), use_container_width=True)
    if st.button("Marcar todas como lidas"):
        safe_run(lambda: _marcar_todas(user), success_message="Notificacoes atualizadas.")
    if notificacoes:
        notificacao_id = st.selectbox("Notificacao", [item.id for item in notificacoes])
        if st.button("Marcar como lida"):
            safe_run(lambda: _marcar(user, notificacao_id), success_message="Notificacao marcada como lida.")


def _marcar(user, notificacao_id):
    with db_session() as db:
        notification_service.marcar_lida(db, notificacao_id, user["id"])


def _marcar_todas(user):
    with db_session() as db:
        notification_service.marcar_todas_lidas(db, user["id"])
