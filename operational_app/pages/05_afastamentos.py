from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.crud import afastamentos as crud_afastamentos
from src.crud import colaboradores as crud_colaboradores


def render(user: dict):
    st.subheader("Afastamentos")
    with db_session() as db:
        colaboradores = crud_colaboradores.listar(db)
        options = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
    if not options:
        st.warning("Cadastre colaboradores antes de registrar afastamentos.")
        return
    with st.form("novo_afastamento"):
        colaborador = st.selectbox("Colaborador", list(options.keys()))
        tipo = st.selectbox("Tipo", ["atestado_medico", "licenca_maternidade", "licenca_paternidade", "inss", "acidente_trabalho", "falta_justificada", "falta_injustificada", "suspensao", "licenca_nao_remunerada", "outros"])
        data_inicio = st.date_input("Data de início")
        data_fim = st.date_input("Data de fim")
        quantidade_dias = st.number_input("Quantidade de dias", min_value=0.0, value=1.0)
        salvar = st.form_submit_button("Registrar afastamento")
    if salvar:
        with db_session() as db:
            crud_afastamentos.criar(
                db,
                {"colaborador_id": options[colaborador], "tipo": tipo, "data_inicio": data_inicio, "data_fim": data_fim, "quantidade_dias": quantidade_dias, "impacta_folha": True, "impacta_absenteismo": True},
                user["id"],
            )
        st.success("Afastamento registrado.")
    with db_session() as db:
        st.dataframe([{"id": item.id, "colaborador_id": item.colaborador_id, "tipo": item.tipo, "inicio": item.data_inicio, "fim": item.data_fim, "dias": item.quantidade_dias} for item in crud_afastamentos.listar(db)], use_container_width=True)
