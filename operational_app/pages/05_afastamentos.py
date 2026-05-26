from __future__ import annotations

import streamlit as st

from operational_app.common import db_session, safe_run, show_warning
from src.crud import afastamentos as crud_afastamentos
from src.crud import colaboradores as crud_colaboradores


TIPOS = ["atestado_medico", "licenca_maternidade", "licenca_paternidade", "inss", "acidente_trabalho", "falta_justificada", "falta_injustificada", "suspensao", "licenca_nao_remunerada", "outros"]


def render(user: dict):
    st.subheader("Afastamentos")
    cadastro_tab, gestao_tab = st.tabs(["Registrar", "Acompanhamento"])
    with cadastro_tab:
        with db_session() as db:
            colaboradores = crud_colaboradores.listar(db)
        options = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
        if not options:
            show_warning("Cadastre colaboradores antes de registrar afastamentos.")
            return
        with st.form("novo_afastamento"):
            colaborador = st.selectbox("Colaborador", list(options.keys()))
            tipo = st.selectbox("Tipo", TIPOS)
            data_inicio = st.date_input("Data de inicio")
            data_fim = st.date_input("Data de fim")
            impacta_folha = st.checkbox("Impacta folha", value=True)
            impacta_absenteismo = st.checkbox("Impacta absenteismo", value=True)
            cid = st.text_input("CID mascarado")
            arquivo = st.file_uploader("Anexar atestado/documento", type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx"])
            salvar = st.form_submit_button("Registrar afastamento")
        if salvar:
            safe_run(
                lambda: _criar_afastamento(user, options[colaborador], tipo, data_inicio, data_fim, impacta_folha, impacta_absenteismo, cid, arquivo),
                success_message="Afastamento registrado.",
                error_prefix="Nao foi possivel registrar afastamento.",
            )
    with gestao_tab:
        with db_session() as db:
            afastamentos = crud_afastamentos.listar(db)
            colaboradores = {item.id: item for item in crud_colaboradores.listar(db)}
        st.dataframe(
            [
                {
                    "id": item.id,
                    "colaborador": colaboradores.get(item.colaborador_id).nome_completo if colaboradores.get(item.colaborador_id) else item.colaborador_id,
                    "tipo": item.tipo,
                    "inicio": item.data_inicio,
                    "fim": item.data_fim,
                    "dias": item.quantidade_dias,
                    "status": item.status,
                }
                for item in afastamentos
            ],
            use_container_width=True,
        )
        ativos = [item for item in afastamentos if item.status == "ativo"]
        if ativos:
            selecionado = st.selectbox("Encerrar afastamento", [f"{item.id} - {colaboradores.get(item.colaborador_id).nome_completo if colaboradores.get(item.colaborador_id) else item.colaborador_id}" for item in ativos])
            afastamento_id = int(selecionado.split(" - ")[0])
            data_fim = st.date_input("Data de retorno", key="retorno_afastamento")
            if st.button("Encerrar afastamento"):
                safe_run(lambda: _encerrar(user, afastamento_id, data_fim), success_message="Afastamento encerrado.")


def _criar_afastamento(user, colaborador_id, tipo, data_inicio, data_fim, impacta_folha, impacta_absenteismo, cid, arquivo):
    with db_session() as db:
        afastamento = crud_afastamentos.criar(
            db,
            {
                "colaborador_id": colaborador_id,
                "tipo": tipo,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "impacta_folha": impacta_folha,
                "impacta_absenteismo": impacta_absenteismo,
                "cid_mascarado": cid,
                "status": "ativo",
            },
            user["id"],
        )
        if arquivo is not None:
            crud_afastamentos.anexar_documento(db, afastamento_id=afastamento.id, original_name=arquivo.name, content=arquivo.getvalue(), usuario_id=user["id"])


def _encerrar(user, afastamento_id, data_fim):
    with db_session() as db:
        crud_afastamentos.encerrar(db, afastamento_id, data_fim, user["id"])
