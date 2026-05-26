from __future__ import annotations

import pandas as pd
import streamlit as st

from operational_app.common import db_session, safe_run
from src.crud import banco_horas as crud_banco_horas
from src.crud import colaboradores as crud_colaboradores


def render(user: dict):
    st.subheader("Banco de Horas")
    with db_session() as db:
        colaboradores = crud_colaboradores.listar(db)
        movimentos = crud_banco_horas.listar_movimentos(db)
        saldos_departamento = crud_banco_horas.saldo_por_departamento(db)
    colab_map = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
    with st.form("movimento_banco_horas"):
        colaborador = st.selectbox("Colaborador", list(colab_map.keys()))
        data_ref = st.date_input("Data")
        origem = st.selectbox("Origem", ["ajuste_manual", "apuracao_ponto", "fechamento_folha", "importacao"])
        tipo = st.selectbox("Tipo", ["credito", "debito", "ajuste"])
        horas = st.text_input("Horas", value="1,50")
        descricao = st.text_area("Descricao")
        salvar = st.form_submit_button("Salvar movimento")
    if salvar:
        safe_run(
            lambda: _salvar(user, colab_map[colaborador], data_ref, origem, tipo, horas, descricao),
            success_message="Movimento de banco de horas registrado.",
        )
    st.markdown("**Movimentos**")
    st.dataframe(pd.DataFrame([{"id": item.id, "colaborador_id": item.colaborador_id, "data": item.data, "tipo": item.tipo, "horas": item.horas, "origem": item.origem} for item in movimentos]), use_container_width=True)
    st.markdown("**Saldo por departamento**")
    st.dataframe(pd.DataFrame(saldos_departamento), use_container_width=True)


def _salvar(user, colaborador_id, data_ref, origem, tipo, horas, descricao):
    with db_session() as db:
        crud_banco_horas.criar_movimento(
            db,
            {"colaborador_id": colaborador_id, "data": data_ref, "origem": origem, "tipo": tipo, "horas": horas, "descricao": descricao},
            user["id"],
        )
