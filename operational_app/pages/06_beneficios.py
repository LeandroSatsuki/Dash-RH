from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.crud import beneficios as crud_beneficios
from src.crud import colaboradores as crud_colaboradores


def render(user: dict):
    st.subheader("Benefícios")
    with db_session() as db:
        beneficios = crud_beneficios.listar(db)
        colaboradores = crud_colaboradores.listar(db)
        map_beneficios = {f"{item.id} - {item.nome}": item.id for item in beneficios}
        map_colabs = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
    if beneficios and colaboradores:
        with st.form("vinculo_beneficio"):
            colaborador = st.selectbox("Colaborador", list(map_colabs.keys()))
            beneficio = st.selectbox("Benefício", list(map_beneficios.keys()))
            valor_empresa = st.number_input("Valor empresa", min_value=0.0, value=0.0)
            valor_colaborador = st.number_input("Valor colaborador", min_value=0.0, value=0.0)
            salvar = st.form_submit_button("Vincular benefício")
        if salvar:
            with db_session() as db:
                crud_beneficios.vincular_ao_colaborador(
                    db,
                    {"colaborador_id": map_colabs[colaborador], "beneficio_id": map_beneficios[beneficio], "valor_empresa": valor_empresa, "valor_colaborador": valor_colaborador, "status": "ativo"},
                    user["id"],
                )
            st.success("Benefício vinculado.")
    else:
        st.info("Cadastre benefícios e colaboradores para criar vínculos.")
