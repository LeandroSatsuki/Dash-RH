from __future__ import annotations

import streamlit as st

from operational_app.common import confirm_action, db_session, safe_run, show_warning
from src.crud import colaboradores as crud_colaboradores
from src.crud import desligamentos as crud_desligamentos


TIPOS = ["pedido_demissao", "dispensa_sem_justa_causa", "dispensa_com_justa_causa", "termino_contrato", "acordo", "falecimento", "aposentadoria", "outros"]


def render(user: dict):
    st.subheader("Desligamentos")
    cadastro_tab, gestao_tab = st.tabs(["Solicitacao", "Gestao"])
    with cadastro_tab:
        with db_session() as db:
            colaboradores = [item for item in crud_colaboradores.listar(db) if item.status != "desligado"]
        mapa = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
        if not mapa:
            show_warning("Nao ha colaboradores elegiveis para desligamento.")
            return
        with st.form("novo_desligamento"):
            colaborador = st.selectbox("Colaborador", list(mapa.keys()))
            data_aviso = st.date_input("Data aviso previo")
            data_desligamento = st.date_input("Data desligamento")
            tipo = st.selectbox("Tipo de rescisao", TIPOS)
            exame = st.checkbox("Exame demissional")
            entrevista = st.checkbox("Entrevista realizada")
            salvar = st.form_submit_button("Registrar desligamento")
        if salvar:
            safe_run(
                lambda: _criar_desligamento(user, mapa[colaborador], data_aviso, data_desligamento, tipo, exame, entrevista),
                success_message="Solicitacao de desligamento registrada.",
                error_prefix="Nao foi possivel registrar desligamento.",
            )
    with gestao_tab:
        with db_session() as db:
            desligamentos = crud_desligamentos.listar(db)
            colaboradores = {item.id: item for item in crud_colaboradores.listar(db)}
        st.dataframe(
            [
                {
                    "id": item.id,
                    "colaborador": colaboradores.get(item.colaborador_id).nome_completo if colaboradores.get(item.colaborador_id) else item.colaborador_id,
                    "data_desligamento": item.data_desligamento,
                    "tipo": item.tipo_rescisao,
                    "status": item.status,
                }
                for item in desligamentos
            ],
            use_container_width=True,
        )
        if not desligamentos:
            return
        selecionado = st.selectbox("Desligamento", [f"{item.id} - {colaboradores.get(item.colaborador_id).nome_completo if colaboradores.get(item.colaborador_id) else item.colaborador_id}" for item in desligamentos])
        desligamento_id = int(selecionado.split(" - ")[0])
        col1, col2 = st.columns(2)
        if col1.button("Concluir desligamento"):
            if confirm_action("Confirmo a conclusao do desligamento", f"confirm_desligamento_{desligamento_id}"):
                safe_run(lambda: _concluir(user, desligamento_id), success_message="Desligamento concluido.")
        if col2.button("Cancelar desligamento"):
            safe_run(lambda: _cancelar(user, desligamento_id), success_message="Desligamento cancelado.")


def _criar_desligamento(user, colaborador_id, data_aviso, data_desligamento, tipo, exame, entrevista):
    with db_session() as db:
        crud_desligamentos.criar(
            db,
            {
                "colaborador_id": colaborador_id,
                "data_aviso_previo": data_aviso,
                "data_desligamento": data_desligamento,
                "tipo_rescisao": tipo,
                "exame_demissional": exame,
                "entrevista_realizada": entrevista,
                "status": "rascunho",
            },
            user["id"],
        )


def _concluir(user, desligamento_id):
    with db_session() as db:
        crud_desligamentos.concluir(db, desligamento_id, user["id"])


def _cancelar(user, desligamento_id):
    with db_session() as db:
        crud_desligamentos.cancelar(db, desligamento_id, user["id"])
