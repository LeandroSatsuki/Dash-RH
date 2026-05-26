from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from operational_app.common import db_session, format_currency, format_percent
from src.crud import centros_custo as crud_centros
from src.crud import departamentos as crud_departamentos
from src.services.indicadores import indicadores_operacionais


def render(user: dict):
    st.subheader("Indicadores Operacionais")
    with db_session() as db:
        departamentos = crud_departamentos.listar(db)
        centros = crud_centros.listar(db)
    ano = st.number_input("Ano", min_value=2020, max_value=2100, value=2026)
    mes = st.number_input("Mes", min_value=1, max_value=12, value=1)
    dept_map = {"Todos": None, **{f"{item.id} - {item.nome}": item.id for item in departamentos}}
    centro_map = {"Todos": None, **{f"{item.id} - {item.nome}": item.id for item in centros}}
    departamento = st.selectbox("Departamento", list(dept_map.keys()))
    centro = st.selectbox("Centro de custo", list(centro_map.keys()))
    regime = st.selectbox("Regime contratual", ["Todos", "CLT", "PJ", "Temporario", "Estagio"])
    status = st.selectbox("Status colaborador", ["Todos", "pre_admissao", "ativo", "afastado", "ferias", "desligado", "inativo"])
    with db_session() as db:
        indicadores = indicadores_operacionais(
            db,
            ano=int(ano),
            mes=int(mes),
            departamento_id=dept_map[departamento],
            centro_custo_id=centro_map[centro],
            regime_contratual=None if regime == "Todos" else regime,
            status_colaborador=None if status == "Todos" else status,
        )
    kpis = indicadores["kpis"]
    cols = st.columns(4)
    cols[0].metric("Colaboradores ativos", kpis["colaboradores_ativos"])
    cols[1].metric("Admissoes no mes", kpis["admissoes_mes"])
    cols[2].metric("Desligamentos no mes", kpis["desligamentos_mes"])
    cols[3].metric("Saldo headcount", kpis["saldo_headcount"])
    cols = st.columns(4)
    cols[0].metric("Turnover", format_percent(kpis["turnover"]))
    cols[1].metric("Afastados ativos", kpis["afastados_ativos"])
    cols[2].metric("Ferias vencidas", kpis["ferias_vencidas"])
    cols[3].metric("Ferias a vencer", kpis["ferias_a_vencer"])
    if user["perfil"] in {"admin", "dp", "financeiro", "diretoria"}:
        cols = st.columns(4)
        cols[0].metric("Folha bruta", format_currency(kpis["folha_bruta"]))
        cols[1].metric("Custo total", format_currency(kpis["custo_total_competencia"]))
        cols[2].metric("Beneficios ativos", kpis["beneficios_ativos"])
        cols[3].metric("Custo beneficios", format_currency(kpis["custo_beneficios"]))
    graficos = indicadores["graficos"]
    _show_chart("Headcount por departamento", graficos["headcount_por_departamento"], "departamento", "total", "bar")
    _show_chart("Admissoes x desligamentos", graficos["admissoes_desligamentos_mes"], "competencia", ["admissoes", "desligamentos"], "line")
    _show_chart("Afastamentos por tipo", graficos["afastamentos_por_tipo"], "tipo", "total", "bar")
    _show_chart("Ferias por status", graficos["ferias_por_status"], "status", "total", "pie")
    if user["perfil"] in {"admin", "dp", "financeiro", "diretoria"}:
        _show_chart("Custo por departamento", graficos["custo_por_departamento"], "departamento", "valor", "bar", currency=True)
        _show_chart("Custo por rubrica", graficos["custo_por_rubrica"], "rubrica_id", "valor", "bar", currency=True)


def _show_chart(title, data, x, y, chart_type, currency: bool = False):
    st.markdown(f"**{title}**")
    if not data:
        st.info("Sem dados para o filtro selecionado.")
        return
    df = pd.DataFrame(data)
    if chart_type == "bar":
        fig = px.bar(df, x=x, y=y)
    elif chart_type == "line":
        fig = px.line(df, x=x, y=y)
    else:
        fig = px.pie(df, names=x, values=y)
    if currency:
        fig.update_yaxes(tickprefix="R$ ")
    st.plotly_chart(fig, use_container_width=True)
