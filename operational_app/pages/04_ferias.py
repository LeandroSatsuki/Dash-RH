from __future__ import annotations

import streamlit as st

from operational_app.common import confirm_action, db_session, safe_run, show_warning
from src.crud import colaboradores as crud_colaboradores
from src.crud import ferias as crud_ferias


def render(user: dict):
    st.subheader("Ferias")
    cadastro_tab, gestao_tab = st.tabs(["Solicitar", "Gestao"])
    with cadastro_tab:
        with db_session() as db:
            colaboradores = crud_colaboradores.listar(db)
        options = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
        if not options:
            show_warning("Cadastre colaboradores antes de registrar ferias.")
            return
        with st.form("nova_ferias"):
            selecionado = st.selectbox("Colaborador", list(options.keys()))
            periodo_inicio = st.date_input("Periodo aquisitivo inicio")
            periodo_fim = st.date_input("Periodo aquisitivo fim")
            data_limite_gozo = st.date_input("Data limite gozo")
            data_inicio = st.date_input("Data de inicio")
            data_fim = st.date_input("Data de fim")
            dias_direito = st.number_input("Dias de direito", min_value=0.0, value=30.0)
            dias_gozados = st.number_input("Dias gozados", min_value=0.0, value=30.0)
            status = st.selectbox("Status", ["planejada", "solicitada", "aprovada", "em_gozo", "concluida", "cancelada", "vencida"])
            salvar = st.form_submit_button("Salvar ferias")
        if salvar:
            safe_run(
                lambda: _criar_ferias(user, options[selecionado], periodo_inicio, periodo_fim, data_limite_gozo, data_inicio, data_fim, dias_direito, dias_gozados, status),
                success_message="Ferias registradas.",
                error_prefix="Nao foi possivel registrar ferias.",
            )

    with gestao_tab:
        with db_session() as db:
            ferias = crud_ferias.listar(db)
            colaboradores = {item.id: item for item in crud_colaboradores.listar(db)}
            alertas_30 = crud_ferias.alertas_a_vencer(db, 30)
            alertas_60 = crud_ferias.alertas_a_vencer(db, 60)
            alertas_90 = crud_ferias.alertas_a_vencer(db, 90)
        st.caption(f"A vencer em 30 dias: {len(alertas_30)} | 60 dias: {len(alertas_60)} | 90 dias: {len(alertas_90)}")
        st.dataframe(
            [
                {
                    "id": item.id,
                    "colaborador": colaboradores.get(item.colaborador_id).nome_completo if colaboradores.get(item.colaborador_id) else item.colaborador_id,
                    "inicio": item.data_inicio,
                    "fim": item.data_fim,
                    "dias_restantes": item.dias_restantes,
                    "status": item.status,
                }
                for item in ferias
            ],
            use_container_width=True,
        )
        if not ferias:
            return
        selecionado = st.selectbox("Ferias", [f"{item.id} - {colaboradores.get(item.colaborador_id).nome_completo if colaboradores.get(item.colaborador_id) else item.colaborador_id}" for item in ferias])
        ferias_id = int(selecionado.split(" - ")[0])
        col1, col2, col3 = st.columns(3)
        if col1.button("Aprovar ferias"):
            if confirm_action("Confirmo a aprovacao das ferias", f"aprovar_ferias_{ferias_id}"):
                safe_run(lambda: _aprovar(user, ferias_id), success_message="Ferias aprovadas.")
        if col2.button("Cancelar ferias"):
            if confirm_action("Confirmo o cancelamento das ferias", f"cancelar_ferias_{ferias_id}"):
                safe_run(lambda: _cancelar(user, ferias_id), success_message="Ferias canceladas.")
        if col3.button("Concluir ferias"):
            safe_run(lambda: _concluir(user, ferias_id), success_message="Ferias concluidas.")


def _criar_ferias(user, colaborador_id, periodo_inicio, periodo_fim, data_limite_gozo, data_inicio, data_fim, dias_direito, dias_gozados, status):
    with db_session() as db:
        crud_ferias.criar(
            db,
            {
                "colaborador_id": colaborador_id,
                "periodo_aquisitivo_inicio": periodo_inicio,
                "periodo_aquisitivo_fim": periodo_fim,
                "data_limite_gozo": data_limite_gozo,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "dias_direito": dias_direito,
                "dias_gozados": dias_gozados,
                "dias_restantes": max(dias_direito - dias_gozados, 0),
                "status": status,
            },
            user["id"],
        )


def _aprovar(user, ferias_id):
    with db_session() as db:
        crud_ferias.aprovar(db, ferias_id, user["id"])


def _cancelar(user, ferias_id):
    with db_session() as db:
        crud_ferias.cancelar(db, ferias_id, user["id"])


def _concluir(user, ferias_id):
    with db_session() as db:
        crud_ferias.concluir(db, ferias_id, user["id"])
