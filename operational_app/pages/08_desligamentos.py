from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.crud import colaboradores as crud_colaboradores
from src.crud import desligamentos as crud_desligamentos


def render(user: dict):
    st.subheader("Desligamentos")
    with db_session() as db:
        colaboradores = crud_colaboradores.listar(db)
        mapa = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
    if not mapa:
        st.info("Cadastre colaboradores primeiro.")
        return
    with st.form("novo_desligamento"):
        colaborador = st.selectbox("Colaborador", list(mapa.keys()))
        data_desligamento = st.date_input("Data do desligamento")
        tipo = st.selectbox("Tipo de rescisão", ["pedido_demissao", "dispensa_sem_justa_causa", "dispensa_com_justa_causa", "termino_contrato", "acordo", "falecimento", "aposentadoria", "outros"])
        salvar = st.form_submit_button("Registrar desligamento")
    if salvar:
        with db_session() as db:
            crud_desligamentos.criar(db, {"colaborador_id": mapa[colaborador], "data_desligamento": data_desligamento, "tipo_rescisao": tipo, "status": "concluida"}, user["id"])
        st.success("Desligamento registrado.")
