from __future__ import annotations

import pandas as pd
import streamlit as st

from operational_app.common import db_session, safe_run
from src.crud import colaboradores as crud_colaboradores
from src.crud import ponto as crud_ponto
from src.services.importacao_ponto import importar_marcacoes, preview_importacao


def render(user: dict):
    st.subheader("Ponto Operacional")
    tab1, tab2, tab3, tab4 = st.tabs(["Marcacoes", "Importacao", "Apuracao", "Ajustes"])
    with tab1:
        with db_session() as db:
            colaboradores = crud_colaboradores.listar(db)
            marcacoes = crud_ponto.listar_marcacoes(db)
        colab_map = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
        with st.form("marcacao_manual"):
            colaborador = st.selectbox("Colaborador", list(colab_map.keys()))
            data_ref = st.date_input("Data")
            tipo = st.selectbox("Tipo", ["entrada", "saida_intervalo", "retorno_intervalo", "saida", "ajuste_manual"])
            horario = st.text_input("Horario", value="08:00")
            salvar = st.form_submit_button("Lancar marcacao")
        if salvar:
            safe_run(
                lambda: _criar_marcacao(user, colab_map[colaborador], data_ref, tipo, horario),
                success_message="Marcacao registrada.",
            )
        st.dataframe(pd.DataFrame([{"id": item.id, "colaborador_id": item.colaborador_id, "data": item.data, "tipo": item.tipo, "horario": item.horario, "origem": item.origem} for item in marcacoes]), use_container_width=True)
    with tab2:
        arquivo = st.file_uploader("Arquivo CSV ou Excel", type=["csv", "xlsx", "xls"], key="ponto_upload")
        if arquivo is not None:
            temp_path = f"data/uploads/{arquivo.name}"
            with open(temp_path, "wb") as target:
                target.write(arquivo.getvalue())
            st.markdown("**Pre-visualizacao**")
            st.dataframe(pd.DataFrame(preview_importacao(temp_path)), use_container_width=True)
            if st.button("Importar marcacoes"):
                safe_run(
                    lambda: _importar(user, temp_path),
                    success_message="Importacao de ponto concluida.",
                )
    with tab3:
        with st.form("apurar_ponto"):
            data_inicio = st.date_input("Data inicio", key="ap_data_inicio")
            data_fim = st.date_input("Data fim", key="ap_data_fim")
            atualizar_banco = st.checkbox("Atualizar banco de horas")
            apurar = st.form_submit_button("Apurar periodo")
        if apurar:
            safe_run(
                lambda: _apurar(user, data_inicio, data_fim, atualizar_banco),
                success_message="Apuracao concluida.",
            )
        with db_session() as db:
            apuracoes = crud_ponto.listar_apuracoes(db)
        st.dataframe(pd.DataFrame([{"id": item.id, "colaborador_id": item.colaborador_id, "data": item.data, "horas_previstas": item.horas_previstas, "horas_trabalhadas": item.horas_trabalhadas, "horas_extras": item.horas_extras, "horas_faltantes": item.horas_faltantes, "status": item.status} for item in apuracoes]), use_container_width=True)
    with tab4:
        with db_session() as db:
            colaboradores = crud_colaboradores.listar(db)
            ajustes = crud_ponto.listar_ajustes(db)
        colab_map = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
        with st.form("novo_ajuste"):
            colaborador = st.selectbox("Colaborador ajuste", list(colab_map.keys()))
            data_ref = st.date_input("Data ajuste")
            tipo_ajuste = st.text_input("Tipo ajuste", value="inclusao_marcacao")
            motivo = st.text_area("Motivo")
            valor_novo = st.text_area("Valor novo")
            salvar_ajuste = st.form_submit_button("Solicitar ajuste")
        if salvar_ajuste:
            safe_run(
                lambda: _criar_ajuste(user, colab_map[colaborador], data_ref, tipo_ajuste, motivo, valor_novo),
                success_message="Ajuste solicitado.",
            )
        st.dataframe(pd.DataFrame([{"id": item.id, "colaborador_id": item.colaborador_id, "data": item.data, "tipo_ajuste": item.tipo_ajuste, "status": item.status} for item in ajustes]), use_container_width=True)
        if ajustes:
            ajuste_id = st.selectbox("Ajuste para acao", [item.id for item in ajustes])
            col1, col2 = st.columns(2)
            if col1.button("Aprovar ajuste"):
                safe_run(lambda: _aprovar(user, ajuste_id), success_message="Ajuste aprovado.")
            if col2.button("Reprovar ajuste"):
                safe_run(lambda: _reprovar(user, ajuste_id), success_message="Ajuste reprovado.")


def _criar_marcacao(user, colaborador_id, data_ref, tipo, horario):
    with db_session() as db:
        crud_ponto.criar_marcacao(
            db,
            {"colaborador_id": colaborador_id, "data": data_ref, "tipo": tipo, "horario": horario, "origem": "manual"},
            user["id"],
        )


def _importar(user, temp_path):
    with db_session() as db:
        return importar_marcacoes(
            db,
            path=temp_path,
            column_map={"matricula": "matricula", "cpf": "cpf", "nome": "nome", "data": "data", "entrada": "entrada", "saida_intervalo": "saida_intervalo", "retorno_intervalo": "retorno_intervalo", "saida": "saida"},
            usuario_id=user["id"],
        )


def _apurar(user, data_inicio, data_fim, atualizar_banco):
    with db_session() as db:
        crud_ponto.apurar_periodo(db, data_inicio=data_inicio, data_fim=data_fim, usuario_id=user["id"], atualizar_banco_horas=atualizar_banco)


def _criar_ajuste(user, colaborador_id, data_ref, tipo_ajuste, motivo, valor_novo):
    with db_session() as db:
        crud_ponto.criar_ajuste(
            db,
            {"colaborador_id": colaborador_id, "data": data_ref, "tipo_ajuste": tipo_ajuste, "motivo": motivo, "valor_novo": valor_novo},
            user["id"],
        )


def _aprovar(user, ajuste_id):
    with db_session() as db:
        crud_ponto.aprovar_ajuste(db, ajuste_id, user["id"])


def _reprovar(user, ajuste_id):
    with db_session() as db:
        crud_ponto.reprovar_ajuste(db, ajuste_id, user["id"])
