from __future__ import annotations

import pandas as pd
import streamlit as st

from operational_app.common import confirm_action, db_session, format_currency, safe_run
from src.crud import colaboradores as crud_colaboradores
from src.crud import folha as crud_folha


TIPOS_RUBRICA = ["provento", "desconto", "encargo", "beneficio", "provisao", "informativo"]
RUBRICAS_MINIMAS = [
    ("SALARIO_BASE", "salario_base", "provento"),
    ("COMISSAO", "comissao", "provento"),
    ("DSR", "dsr", "provento"),
    ("HORA_EXTRA", "hora_extra", "provento"),
    ("PREMIO", "premio", "provento"),
    ("AJUDA_CUSTO", "ajuda_custo", "beneficio"),
    ("VALE_TRANSPORTE", "vale_transporte", "beneficio"),
    ("VALE_REFEICAO", "vale_refeicao", "beneficio"),
    ("VALE_ALIMENTACAO", "vale_alimentacao", "beneficio"),
    ("PLANO_SAUDE", "plano_saude", "beneficio"),
    ("FGTS", "fgts", "encargo"),
    ("INSS_PATRONAL", "inss_patronal", "encargo"),
    ("PROV_FERIAS", "provisao_ferias", "provisao"),
    ("PROV_13", "provisao_13", "provisao"),
    ("DESCONTO", "desconto", "desconto"),
    ("OUTROS", "outros", "informativo"),
]


def render(user: dict):
    st.subheader("Folha")
    tab1, tab2, tab3 = st.tabs(["Competencias", "Lancamentos", "Resumo"])
    with tab1:
        with st.form("abrir_competencia"):
            ano = st.number_input("Ano", min_value=2020, max_value=2100, value=2026)
            mes = st.number_input("Mes", min_value=1, max_value=12, value=1)
            salvar = st.form_submit_button("Abrir competencia")
        if salvar:
            safe_run(lambda: _abrir_competencia(user, int(ano), int(mes)), success_message="Competencia aberta.")
        if st.button("Garantir rubricas minimas"):
            safe_run(lambda: _garantir_rubricas(user), success_message="Rubricas verificadas.")
        with db_session() as db:
            competencias = crud_folha.listar_competencias(db)
        st.dataframe([{"id": item.id, "competencia": item.competencia, "status": item.status} for item in competencias], use_container_width=True)
        if competencias:
            selected = st.selectbox("Competencia para acao", [f"{item.id} - {item.competencia} ({item.status})" for item in competencias], key="comp_action")
            comp_id = int(selected.split(" - ")[0])
            col1, col2 = st.columns(2)
            if col1.button("Fechar competencia"):
                if confirm_action("Confirmo o fechamento da competencia", f"confirm_fechar_{comp_id}"):
                    safe_run(lambda: _fechar(user, comp_id), success_message="Competencia fechada.")
            if col2.button("Reabrir competencia"):
                if confirm_action("Confirmo a reabertura da competencia", f"confirm_reabrir_{comp_id}"):
                    safe_run(lambda: _reabrir(user, comp_id), success_message="Competencia reaberta.")
    with tab2:
        with db_session() as db:
            competencias = crud_folha.listar_competencias(db)
            rubricas = crud_folha.listar_rubricas(db)
            colaboradores = crud_colaboradores.listar(db)
            lancamentos = crud_folha.listar_lancamentos(db)
        if not (competencias and rubricas and colaboradores):
            st.info("Cadastre competencia, rubrica e colaborador para lancar folha.")
            return
        comp_map = {f"{item.id} - {item.competencia}": item.id for item in competencias}
        rub_map = {f"{item.id} - {item.descricao}": item.id for item in rubricas}
        colab_map = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
        with st.form("novo_lancamento"):
            competencia = st.selectbox("Competencia", list(comp_map.keys()))
            colaborador = st.selectbox("Colaborador", list(colab_map.keys()))
            rubrica = st.selectbox("Rubrica", list(rub_map.keys()))
            tipo = st.selectbox("Tipo", TIPOS_RUBRICA)
            valor = st.text_input("Valor", value="0,00")
            salvar = st.form_submit_button("Lancar")
        if salvar:
            safe_run(
                lambda: _criar_lancamento(user, comp_map[competencia], colab_map[colaborador], rub_map[rubrica], tipo, valor),
                success_message="Lancamento registrado.",
            )
        st.dataframe([{"id": item.id, "competencia_id": item.competencia_id, "colaborador_id": item.colaborador_id, "rubrica_id": item.rubrica_id, "tipo": item.tipo, "valor": format_currency(item.valor)} for item in lancamentos], use_container_width=True)
    with tab3:
        with db_session() as db:
            competencias = crud_folha.listar_competencias(db)
        if not competencias:
            st.info("Nenhuma competencia cadastrada.")
            return
        selecionada = st.selectbox("Competencia", [f"{item.id} - {item.competencia}" for item in competencias], key="resumo_competencia")
        comp_id = int(selecionada.split(" - ")[0])
        with db_session() as db:
            resumo = crud_folha.resumo_competencia(db, comp_id)
            exportacao = crud_folha.exportar_competencia(db, comp_id)
        cols = st.columns(3)
        cols[0].metric("Folha bruta", format_currency(resumo["total_proventos"]))
        cols[1].metric("Encargos", format_currency(resumo["total_encargos"]))
        cols[2].metric("Custo total", format_currency(resumo["total_custo_empresa"]))
        st.dataframe(pd.DataFrame(exportacao), use_container_width=True)


def _abrir_competencia(user, ano, mes):
    competencia = f"{ano:04d}-{mes:02d}"
    with db_session() as db:
        crud_folha.criar_competencia(db, {"ano": ano, "mes": mes, "competencia": competencia, "status": "aberta"}, user["id"])


def _garantir_rubricas(user):
    with db_session() as db:
        existentes = {item.codigo for item in crud_folha.listar_rubricas(db)}
        for codigo, descricao, tipo in RUBRICAS_MINIMAS:
            if codigo not in existentes:
                crud_folha.criar_rubrica(db, {"codigo": codigo, "descricao": descricao, "tipo": tipo}, user["id"])


def _fechar(user, competencia_id):
    with db_session() as db:
        crud_folha.fechar_competencia(db, competencia_id, user["id"])


def _reabrir(user, competencia_id):
    with db_session() as db:
        crud_folha.reabrir_competencia(db, competencia_id, user["id"])


def _criar_lancamento(user, competencia_id, colaborador_id, rubrica_id, tipo, valor):
    with db_session() as db:
        crud_folha.criar_lancamento(
            db,
            {"competencia_id": competencia_id, "colaborador_id": colaborador_id, "rubrica_id": rubrica_id, "tipo": tipo, "valor": valor, "origem": "manual"},
            user["id"],
        )
