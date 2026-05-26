from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.crud import colaboradores as crud_colaboradores
from src.crud import ferias as crud_ferias


def render(user: dict):
    st.subheader("Férias")
    with db_session() as db:
        colaboradores = crud_colaboradores.listar(db)
        options = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
    if not options:
        st.warning("Cadastre colaboradores antes de registrar férias.")
        return
    with st.form("nova_ferias"):
        selecionado = st.selectbox("Colaborador", list(options.keys()))
        data_inicio = st.date_input("Data de início")
        data_fim = st.date_input("Data de fim")
        dias_direito = st.number_input("Dias de direito", min_value=0.0, value=30.0)
        salvar = st.form_submit_button("Registrar férias")
    if salvar:
        with db_session() as db:
            crud_ferias.criar(
                db,
                {
                    "colaborador_id": options[selecionado],
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "dias_direito": dias_direito,
                    "dias_gozados": dias_direito,
                    "dias_restantes": 0.0,
                    "status": "aprovada",
                },
                user["id"],
            )
        st.success("Férias registradas.")
    with db_session() as db:
        st.dataframe([{"id": item.id, "colaborador_id": item.colaborador_id, "inicio": item.data_inicio, "fim": item.data_fim, "status": item.status} for item in crud_ferias.listar(db)], use_container_width=True)
