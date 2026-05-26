from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.crud import colaboradores as crud_colaboradores
from src.crud import folha as crud_folha


def render(user: dict):
    st.subheader("Folha")
    tab1, tab2 = st.tabs(["Competências", "Lançamentos"])
    with tab1:
        with st.form("abrir_competencia"):
            ano = st.number_input("Ano", min_value=2020, max_value=2100, value=2026)
            mes = st.number_input("Mês", min_value=1, max_value=12, value=1)
            salvar = st.form_submit_button("Abrir competência")
        if salvar:
            competencia = f"{int(ano):04d}-{int(mes):02d}"
            with db_session() as db:
                crud_folha.criar_competencia(db, {"ano": int(ano), "mes": int(mes), "competencia": competencia, "status": "aberta"}, user["id"])
            st.success("Competência aberta.")
        with db_session() as db:
            competencias = crud_folha.listar_competencias(db)
            st.dataframe([{"id": item.id, "competencia": item.competencia, "status": item.status} for item in competencias], use_container_width=True)
            if competencias:
                selected = st.selectbox("Competência para ação", [f"{item.id} - {item.competencia} ({item.status})" for item in competencias], key="comp_action")
                comp_id = int(selected.split(" - ")[0])
                col1, col2 = st.columns(2)
                if col1.button("Fechar competência"):
                    crud_folha.fechar_competencia(db, comp_id, user["id"])
                    st.success("Competência fechada.")
                if col2.button("Reabrir competência"):
                    crud_folha.reabrir_competencia(db, comp_id, user["id"])
                    st.success("Competência reaberta.")
    with tab2:
        with db_session() as db:
            competencias = crud_folha.listar_competencias(db)
            rubricas = crud_folha.listar_rubricas(db)
            colaboradores = crud_colaboradores.listar(db)
        if not (competencias and rubricas and colaboradores):
            st.info("Cadastre competência, rubrica e colaborador para lançar folha.")
            return
        comp_map = {f"{item.id} - {item.competencia}": item.id for item in competencias}
        rub_map = {f"{item.id} - {item.descricao}": item.id for item in rubricas}
        colab_map = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
        with st.form("novo_lancamento"):
            competencia = st.selectbox("Competência", list(comp_map.keys()))
            colaborador = st.selectbox("Colaborador", list(colab_map.keys()))
            rubrica = st.selectbox("Rubrica", list(rub_map.keys()))
            tipo = st.selectbox("Tipo", ["provento", "desconto", "encargo", "beneficio", "provisao", "informativo"])
            valor = st.number_input("Valor", value=0.0, step=100.0)
            salvar = st.form_submit_button("Lançar")
        if salvar:
            with db_session() as db:
                crud_folha.criar_lancamento(
                    db,
                    {"competencia_id": comp_map[competencia], "colaborador_id": colab_map[colaborador], "rubrica_id": rub_map[rubrica], "tipo": tipo, "valor": valor, "origem": "manual"},
                    user["id"],
                )
            st.success("Lançamento registrado.")
