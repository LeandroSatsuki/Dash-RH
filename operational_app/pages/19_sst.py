from __future__ import annotations

import pandas as pd
import streamlit as st

from operational_app.common import db_session, safe_run
from src.crud import colaboradores as crud_colaboradores
from src.crud import sst as crud_sst


def render(user: dict):
    st.subheader("SST Operacional")
    tab1, tab2, tab3 = st.tabs(["Exames", "EPIs", "Treinamentos"])
    with tab1:
        with db_session() as db:
            colaboradores = crud_colaboradores.listar(db)
            exames = crud_sst.listar_exames(db)
        colab_map = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
        with st.form("novo_exame"):
            colaborador = st.selectbox("Colaborador", list(colab_map.keys()))
            tipo = st.selectbox("Tipo exame", ["admissional", "periodico", "retorno_trabalho", "mudanca_risco", "demissional"])
            data_exame = st.date_input("Data exame")
            data_validade = st.date_input("Data validade")
            clinica = st.text_input("Clinica")
            salvar = st.form_submit_button("Registrar exame")
        if salvar:
            safe_run(lambda: _exame(user, colab_map[colaborador], tipo, data_exame, data_validade, clinica), success_message="Exame registrado.")
        st.dataframe(pd.DataFrame([{"id": item.id, "colaborador_id": item.colaborador_id, "tipo_exame": item.tipo_exame, "data_exame": item.data_exame, "data_validade": item.data_validade, "status": item.status} for item in exames]), use_container_width=True)
    with tab2:
        with db_session() as db:
            epis = crud_sst.listar_epis(db)
            colaboradores = crud_colaboradores.listar(db)
            entregas = crud_sst.listar_entregas_epi(db)
        with st.form("novo_epi"):
            nome = st.text_input("Nome EPI")
            ca = st.text_input("CA")
            validade_ca = st.date_input("Validade CA")
            salvar_epi = st.form_submit_button("Cadastrar EPI")
        if salvar_epi:
            safe_run(lambda: _epi(user, nome, ca, validade_ca), success_message="EPI cadastrado.")
        st.dataframe(pd.DataFrame([{"id": item.id, "nome": item.nome, "ca": item.ca, "validade_ca": item.validade_ca} for item in epis]), use_container_width=True)
        if epis and colaboradores:
            epi_map = {f"{item.id} - {item.nome}": item.id for item in epis}
            colab_map = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
            with st.form("entrega_epi"):
                colaborador = st.selectbox("Colaborador entrega", list(colab_map.keys()))
                epi = st.selectbox("EPI", list(epi_map.keys()))
                data_entrega = st.date_input("Data entrega")
                quantidade = st.number_input("Quantidade", min_value=1, value=1)
                salvar_entrega = st.form_submit_button("Registrar entrega")
            if salvar_entrega:
                safe_run(lambda: _entrega(user, colab_map[colaborador], epi_map[epi], data_entrega, int(quantidade)), success_message="Entrega de EPI registrada.")
        st.dataframe(pd.DataFrame([{"id": item.id, "colaborador_id": item.colaborador_id, "epi_id": item.epi_id, "data_entrega": item.data_entrega, "status": item.status} for item in entregas]), use_container_width=True)
    with tab3:
        with db_session() as db:
            treinamentos = crud_sst.listar_treinamentos(db)
            colaboradores = crud_colaboradores.listar(db)
            vinculos = crud_sst.listar_colaborador_treinamentos(db)
        with st.form("novo_treinamento"):
            nome = st.text_input("Nome treinamento")
            validade_meses = st.number_input("Validade meses", min_value=1, value=12)
            salvar_treinamento = st.form_submit_button("Cadastrar treinamento")
        if salvar_treinamento:
            safe_run(lambda: _treinamento(user, nome, int(validade_meses)), success_message="Treinamento cadastrado.")
        st.dataframe(pd.DataFrame([{"id": item.id, "nome": item.nome, "validade_meses": item.validade_meses} for item in treinamentos]), use_container_width=True)
        if treinamentos and colaboradores:
            tr_map = {f"{item.id} - {item.nome}": item.id for item in treinamentos}
            colab_map = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
            with st.form("vinculo_treinamento"):
                colaborador = st.selectbox("Colaborador treinamento", list(colab_map.keys()))
                treinamento = st.selectbox("Treinamento", list(tr_map.keys()))
                data_realizacao = st.date_input("Data realizacao")
                data_validade = st.date_input("Data validade treinamento")
                salvar_vinculo = st.form_submit_button("Vincular treinamento")
            if salvar_vinculo:
                safe_run(lambda: _vinculo(user, colab_map[colaborador], tr_map[treinamento], data_realizacao, data_validade), success_message="Treinamento vinculado.")
        st.dataframe(pd.DataFrame([{"id": item.id, "colaborador_id": item.colaborador_id, "treinamento_id": item.treinamento_id, "data_validade": item.data_validade, "status": item.status} for item in vinculos]), use_container_width=True)


def _exame(user, colaborador_id, tipo, data_exame, data_validade, clinica):
    with db_session() as db:
        crud_sst.criar_exame(db, {"colaborador_id": colaborador_id, "tipo_exame": tipo, "data_exame": data_exame, "data_validade": data_validade, "clinica": clinica, "status": "ativo"}, user["id"])


def _epi(user, nome, ca, validade_ca):
    with db_session() as db:
        crud_sst.criar_epi(db, {"nome": nome, "ca": ca, "validade_ca": validade_ca, "ativo": True}, user["id"])


def _entrega(user, colaborador_id, epi_id, data_entrega, quantidade):
    with db_session() as db:
        crud_sst.criar_entrega_epi(db, {"colaborador_id": colaborador_id, "epi_id": epi_id, "data_entrega": data_entrega, "quantidade": quantidade, "status": "ativo"}, user["id"])


def _treinamento(user, nome, validade_meses):
    with db_session() as db:
        crud_sst.criar_treinamento(db, {"nome": nome, "validade_meses": validade_meses, "ativo": True}, user["id"])


def _vinculo(user, colaborador_id, treinamento_id, data_realizacao, data_validade):
    with db_session() as db:
        crud_sst.vincular_treinamento(db, {"colaborador_id": colaborador_id, "treinamento_id": treinamento_id, "data_realizacao": data_realizacao, "data_validade": data_validade, "status": "ativo"}, user["id"])
