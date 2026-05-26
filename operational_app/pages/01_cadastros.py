from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.crud import beneficios, cargos, centros_custo, folha
from src.crud import departamentos as crud_departamentos


def render(user: dict):
    st.subheader("Cadastros")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Departamentos", "Cargos", "Centros de custo", "Rubricas", "Benefícios"])
    with tab1:
        with st.form("novo_departamento"):
            nome = st.text_input("Nome do departamento")
            descricao = st.text_area("Descrição")
            submitted = st.form_submit_button("Salvar departamento")
        if submitted and nome:
            with db_session() as db:
                crud_departamentos.criar(db, {"nome": nome, "descricao": descricao, "status": "ativo"}, user["id"])
            st.success("Departamento cadastrado.")
        with db_session() as db:
            st.dataframe([{"id": item.id, "nome": item.nome, "status": item.status} for item in crud_departamentos.listar(db)], use_container_width=True)
    with tab2:
        with st.form("novo_cargo"):
            nome = st.text_input("Nome do cargo")
            cbo = st.text_input("CBO")
            submitted = st.form_submit_button("Salvar cargo")
        if submitted and nome:
            with db_session() as db:
                cargos.criar(db, {"nome": nome, "cbo": cbo, "status": "ativo"}, user["id"])
            st.success("Cargo cadastrado.")
        with db_session() as db:
            st.dataframe([{"id": item.id, "nome": item.nome, "cbo": item.cbo} for item in cargos.listar(db)], use_container_width=True)
    with tab3:
        with st.form("novo_cc"):
            codigo = st.text_input("Código")
            nome = st.text_input("Nome")
            area = st.text_input("Área")
            subarea = st.text_input("Subárea")
            submitted = st.form_submit_button("Salvar centro de custo")
        if submitted and codigo and nome:
            with db_session() as db:
                centros_custo.criar(db, {"codigo": codigo, "nome": nome, "area": area, "subarea": subarea, "status": "ativo"}, user["id"])
            st.success("Centro de custo cadastrado.")
        with db_session() as db:
            st.dataframe([{"id": item.id, "codigo": item.codigo, "nome": item.nome, "area": item.area, "subarea": item.subarea} for item in centros_custo.listar(db)], use_container_width=True)
    with tab4:
        with st.form("nova_rubrica"):
            codigo = st.text_input("Código da rubrica")
            descricao = st.text_input("Descrição da rubrica")
            tipo = st.selectbox("Tipo", ["provento", "desconto", "encargo", "beneficio", "provisao", "informativo"])
            submitted = st.form_submit_button("Salvar rubrica")
        if submitted and codigo and descricao:
            with db_session() as db:
                folha.criar_rubrica(db, {"codigo": codigo, "descricao": descricao, "tipo": tipo}, user["id"])
            st.success("Rubrica cadastrada.")
        with db_session() as db:
            st.dataframe([{"id": item.id, "codigo": item.codigo, "descricao": item.descricao, "tipo": item.tipo} for item in folha.listar_rubricas(db)], use_container_width=True)
    with tab5:
        with st.form("novo_beneficio"):
            nome = st.text_input("Nome do benefício")
            tipo = st.text_input("Tipo")
            operadora = st.text_input("Operadora")
            submitted = st.form_submit_button("Salvar benefício")
        if submitted and nome:
            with db_session() as db:
                beneficios.criar(db, {"nome": nome, "tipo": tipo, "operadora": operadora, "status": "ativo"}, user["id"])
            st.success("Benefício cadastrado.")
        with db_session() as db:
            st.dataframe([{"id": item.id, "nome": item.nome, "tipo": item.tipo, "operadora": item.operadora} for item in beneficios.listar(db)], use_container_width=True)
