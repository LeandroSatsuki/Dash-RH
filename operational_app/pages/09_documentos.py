from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.crud import colaboradores as crud_colaboradores
from src.crud import documentos as crud_documentos
from src.services.audit_service import log_action
from src.services.file_storage import save_upload


def render(user: dict):
    st.subheader("Documentos")
    with db_session() as db:
        colaboradores = crud_colaboradores.listar(db)
        mapa = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
    if not mapa:
        st.info("Cadastre colaboradores antes de anexar documentos.")
        return
    arquivo = st.file_uploader("Selecione um documento")
    colaborador = st.selectbox("Colaborador", list(mapa.keys()))
    tipo_documento = st.text_input("Tipo de documento")
    validade = st.date_input("Validade")
    if st.button("Salvar documento") and arquivo is not None and tipo_documento:
        conteudo = arquivo.getvalue()
        payload = save_upload(arquivo.name, conteudo)
        with db_session() as db:
            registro = crud_documentos.criar(
                db,
                {
                    "colaborador_id": mapa[colaborador],
                    "tipo_documento": tipo_documento,
                    **payload,
                    "validade": validade,
                    "status": "ativo",
                    "usuario_upload_id": user["id"],
                },
                user["id"],
            )
            log_action(db, tabela="documentos", acao="upload_documento", registro_id=registro.id, usuario_id=user["id"], origem="streamlit", valor_novo={"nome_original": arquivo.name, "tipo_documento": tipo_documento})
        st.success("Documento salvo.")
    with db_session() as db:
        itens = crud_documentos.listar(db)
        st.dataframe(
            [{"id": item.id, "colaborador_id": item.colaborador_id, "tipo": item.tipo_documento, "arquivo": item.nome_original, "validade": item.validade, "status": item.status} for item in itens],
            use_container_width=True,
        )
