from __future__ import annotations

import pandas as pd
import streamlit as st

from operational_app.common import db_session, safe_run
from src.crud import colaboradores as crud_colaboradores
from src.crud import jornadas as crud_jornadas


def render(user: dict):
    st.subheader("Jornadas")
    tab1, tab2, tab3 = st.tabs(["Jornadas", "Turnos", "Vinculos"])
    with tab1:
        with st.form("nova_jornada"):
            nome = st.text_input("Nome")
            descricao = st.text_area("Descricao")
            carga_semanal = st.text_input("Carga semanal", value="44")
            carga_diaria = st.text_input("Carga diaria", value="8")
            salvar = st.form_submit_button("Salvar jornada")
        if salvar:
            safe_run(
                lambda: _criar_jornada(user, nome, descricao, carga_semanal, carga_diaria),
                success_message="Jornada cadastrada.",
            )
        with db_session() as db:
            jornadas = crud_jornadas.listar_jornadas(db)
        st.dataframe(pd.DataFrame([{"id": item.id, "nome": item.nome, "carga_semanal": item.carga_horaria_semanal, "ativo": item.ativo} for item in jornadas]), use_container_width=True)
    with tab2:
        with db_session() as db:
            jornadas = crud_jornadas.listar_jornadas(db)
        if not jornadas:
            st.info("Cadastre uma jornada antes de incluir turnos.")
            return
        jornada_map = {f"{item.id} - {item.nome}": item.id for item in jornadas}
        with st.form("novo_turno"):
            jornada = st.selectbox("Jornada", list(jornada_map.keys()))
            dia_semana = st.selectbox("Dia da semana", list(range(7)), format_func=lambda item: ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"][item])
            descanso = st.checkbox("Descanso")
            noturno = st.checkbox("Noturno")
            entrada = st.text_input("Entrada", value="08:00")
            saida_intervalo = st.text_input("Saida intervalo", value="12:00")
            retorno_intervalo = st.text_input("Retorno intervalo", value="13:00")
            saida = st.text_input("Saida", value="17:00")
            salvar_turno = st.form_submit_button("Salvar turno")
        if salvar_turno:
            safe_run(
                lambda: _criar_turno(user, jornada_map[jornada], dia_semana, descanso, noturno, entrada, saida_intervalo, retorno_intervalo, saida),
                success_message="Turno registrado.",
            )
    with tab3:
        with db_session() as db:
            jornadas = crud_jornadas.listar_jornadas(db)
            colaboradores = crud_colaboradores.listar(db)
        if not jornadas or not colaboradores:
            st.info("Cadastre jornada e colaborador antes de vincular.")
            return
        jornada_map = {f"{item.id} - {item.nome}": item.id for item in jornadas}
        colab_map = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
        with st.form("vinculo_jornada"):
            colaborador = st.selectbox("Colaborador", list(colab_map.keys()))
            jornada = st.selectbox("Jornada ativa", list(jornada_map.keys()), key="jornada_vinculo")
            data_inicio = st.date_input("Data inicio")
            observacao = st.text_area("Observacao")
            salvar_vinculo = st.form_submit_button("Vincular")
        if salvar_vinculo:
            safe_run(
                lambda: _vincular(user, colab_map[colaborador], jornada_map[jornada], data_inicio, observacao),
                success_message="Jornada vinculada ao colaborador.",
            )
        st.markdown("**Jornada atual por colaborador**")
        linhas = []
        with db_session() as db:
            for colaborador_id in colab_map.values():
                atual = crud_jornadas.jornada_atual_colaborador(db, colaborador_id)
                if atual is not None:
                    linhas.append({"colaborador_id": colaborador_id, "jornada_id": atual.jornada_id, "data_inicio": atual.data_inicio, "data_fim": atual.data_fim})
        st.dataframe(pd.DataFrame(linhas), use_container_width=True)


def _criar_jornada(user, nome, descricao, carga_semanal, carga_diaria):
    with db_session() as db:
        crud_jornadas.criar_jornada(
            db,
            {
                "nome": nome,
                "descricao": descricao,
                "carga_horaria_semanal": carga_semanal,
                "carga_horaria_diaria": carga_diaria,
                "tolerancia_entrada_minutos": 10,
                "tolerancia_saida_minutos": 10,
                "intervalo_minimo_minutos": 60,
                "ativo": True,
            },
            user["id"],
        )


def _criar_turno(user, jornada_id, dia_semana, descanso, noturno, entrada, saida_intervalo, retorno_intervalo, saida):
    with db_session() as db:
        crud_jornadas.criar_turno(
            db,
            jornada_id,
            {
                "dia_semana": dia_semana,
                "descanso": descanso,
                "noturno": noturno,
                "hora_entrada": None if descanso else entrada,
                "hora_saida_intervalo": None if descanso else saida_intervalo,
                "hora_retorno_intervalo": None if descanso else retorno_intervalo,
                "hora_saida": None if descanso else saida,
            },
            user["id"],
        )


def _vincular(user, colaborador_id, jornada_id, data_inicio, observacao):
    with db_session() as db:
        crud_jornadas.vincular_jornada_colaborador(
            db,
            colaborador_id,
            {"jornada_id": jornada_id, "data_inicio": data_inicio, "observacao": observacao, "ativo": True},
            user["id"],
        )
