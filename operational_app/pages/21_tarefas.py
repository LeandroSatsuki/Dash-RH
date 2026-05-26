from __future__ import annotations

import pandas as pd
import streamlit as st

from operational_app.common import db_session, safe_run
from src.crud import tarefas as crud_tarefas
from src.services import task_service


def render(user: dict):
    st.subheader("Tarefas Operacionais")
    tab1, tab2 = st.tabs(["Lista", "Nova tarefa"])
    with tab1:
        with db_session() as db:
            tarefas = crud_tarefas.listar(db)
        st.dataframe(pd.DataFrame([{"id": item.id, "titulo": item.titulo, "modulo": item.modulo, "status": item.status, "prioridade": item.prioridade, "responsavel_id": item.responsavel_id, "prazo": item.prazo} for item in tarefas]), use_container_width=True)
        if tarefas:
            tarefa_id = st.selectbox("Tarefa", [item.id for item in tarefas])
            comentario = st.text_area("Comentario")
            col1, col2, col3 = st.columns(3)
            if col1.button("Comentar"):
                safe_run(lambda: _comentar(user, tarefa_id, comentario), success_message="Comentario registrado.")
            if col2.button("Concluir"):
                safe_run(lambda: _concluir(user, tarefa_id), success_message="Tarefa concluida.")
            if col3.button("Cancelar"):
                safe_run(lambda: _cancelar(user, tarefa_id, comentario), success_message="Tarefa cancelada.")
    with tab2:
        with st.form("nova_tarefa"):
            titulo = st.text_input("Titulo")
            descricao = st.text_area("Descricao")
            modulo = st.text_input("Modulo", value="geral")
            prioridade = st.selectbox("Prioridade", ["baixa", "media", "alta", "critica"])
            responsavel_id = st.number_input("Responsavel ID", min_value=1, value=1)
            prazo = st.date_input("Prazo")
            salvar = st.form_submit_button("Criar tarefa")
        if salvar:
            safe_run(lambda: _criar(user, titulo, descricao, modulo, prioridade, responsavel_id, prazo), success_message="Tarefa criada.")


def _criar(user, titulo, descricao, modulo, prioridade, responsavel_id, prazo):
    from datetime import datetime

    with db_session() as db:
        task_service.create_task(
            db,
            {
                "titulo": titulo,
                "descricao": descricao,
                "modulo": modulo,
                "prioridade": prioridade,
                "responsavel_id": int(responsavel_id),
                "solicitante_id": user["id"],
                "prazo": datetime.combine(prazo, datetime.min.time()),
            },
            user["id"],
        )


def _comentar(user, tarefa_id, comentario):
    with db_session() as db:
        task_service.comment_task(db, tarefa_id, comentario, user["id"])


def _concluir(user, tarefa_id):
    with db_session() as db:
        task_service.complete_task(db, tarefa_id, user["id"])


def _cancelar(user, tarefa_id, comentario):
    with db_session() as db:
        task_service.cancel_task(db, tarefa_id, comentario, user["id"])
