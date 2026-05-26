from __future__ import annotations

import pandas as pd
import streamlit as st

from operational_app.common import db_session, safe_run
from src.crud import cargos as crud_cargos
from src.crud import departamentos as crud_departamentos
from src.crud import documentos_obrigatorios as crud_docs


def render(user: dict):
    st.subheader("Documentos Obrigatorios")
    tab1, tab2, tab3 = st.tabs(["Tipos", "Regras", "Pendencias"])
    with tab1:
        with st.form("tipo_documento"):
            nome = st.text_input("Nome")
            descricao = st.text_area("Descricao")
            sensivel = st.checkbox("Sensivel")
            exige_validade = st.checkbox("Exige validade")
            salvar = st.form_submit_button("Salvar tipo")
        if salvar:
            safe_run(lambda: _tipo(user, nome, descricao, sensivel, exige_validade), success_message="Tipo de documento cadastrado.")
        with db_session() as db:
            tipos = crud_docs.listar_tipos_documento(db)
        st.dataframe(pd.DataFrame([{"id": item.id, "nome": item.nome, "sensivel": item.sensivel, "exige_validade": item.exige_validade} for item in tipos]), use_container_width=True)
    with tab2:
        with db_session() as db:
            tipos = crud_docs.listar_tipos_documento(db)
            cargos = crud_cargos.listar(db)
            departamentos = crud_departamentos.listar(db)
        if not tipos:
            st.info("Cadastre ao menos um tipo de documento.")
        else:
            tipo_map = {f"{item.id} - {item.nome}": item.id for item in tipos}
            cargo_map = {"Todos": None, **{f"{item.id} - {item.nome}": item.id for item in cargos}}
            dept_map = {"Todos": None, **{f"{item.id} - {item.nome}": item.id for item in departamentos}}
            with st.form("regra_documento"):
                tipo = st.selectbox("Tipo documento", list(tipo_map.keys()))
                regime = st.selectbox("Regime contratual", ["Todos", "CLT", "PJ", "Temporario"])
                cargo = st.selectbox("Cargo", list(cargo_map.keys()))
                departamento = st.selectbox("Departamento", list(dept_map.keys()))
                validade_dias = st.number_input("Validade em dias", min_value=0, value=365)
                salvar_regra = st.form_submit_button("Salvar regra")
            if salvar_regra:
                safe_run(
                    lambda: _regra(user, tipo_map[tipo], None if regime == "Todos" else regime, cargo_map[cargo], dept_map[departamento], int(validade_dias)),
                    success_message="Regra cadastrada.",
                )
        with db_session() as db:
            regras = crud_docs.listar_regras(db)
        st.dataframe(pd.DataFrame([{"id": item.id, "tipo_documento_id": item.tipo_documento_id, "regime": item.regime_contratual, "cargo_id": item.cargo_id, "departamento_id": item.departamento_id, "validade_dias": item.validade_dias} for item in regras]), use_container_width=True)
    with tab3:
        if st.button("Gerar pendencias"):
            safe_run(lambda: _gerar(user), success_message="Pendencias geradas.")
        with db_session() as db:
            pendencias = crud_docs.listar_pendencias(db)
        st.dataframe(pd.DataFrame([{"id": item.id, "colaborador_id": item.colaborador_id, "tipo_documento_id": item.tipo_documento_id, "status": item.status, "severidade": item.severidade, "vencimento": item.data_vencimento} for item in pendencias]), use_container_width=True)
        if pendencias:
            pendencia_id = st.selectbox("Pendencia", [item.id for item in pendencias])
            col1, col2 = st.columns(2)
            if col1.button("Aprovar pendencia"):
                safe_run(lambda: _aprovar(user, pendencia_id), success_message="Pendencia aprovada.")
            justificativa = st.text_input("Justificativa dispensa", value="Dispensa operacional.")
            if col2.button("Dispensar pendencia"):
                safe_run(lambda: _dispensar(user, pendencia_id, justificativa), success_message="Pendencia dispensada.")


def _tipo(user, nome, descricao, sensivel, exige_validade):
    with db_session() as db:
        crud_docs.criar_tipo_documento(db, {"nome": nome, "descricao": descricao, "sensivel": sensivel, "exige_validade": exige_validade, "ativo": True}, user["id"])


def _regra(user, tipo_documento_id, regime, cargo_id, departamento_id, validade_dias):
    with db_session() as db:
        crud_docs.criar_regra(
            db,
            {"tipo_documento_id": tipo_documento_id, "regime_contratual": regime, "cargo_id": cargo_id, "departamento_id": departamento_id, "obrigatorio": True, "validade_dias": validade_dias},
            user["id"],
        )


def _gerar(user):
    with db_session() as db:
        crud_docs.gerar_pendencias(db, user["id"])


def _aprovar(user, pendencia_id):
    with db_session() as db:
        crud_docs.aprovar_pendencia(db, pendencia_id, user["id"])


def _dispensar(user, pendencia_id, justificativa):
    with db_session() as db:
        crud_docs.dispensar_pendencia(db, pendencia_id, justificativa, user["id"])
