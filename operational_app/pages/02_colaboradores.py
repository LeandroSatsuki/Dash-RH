from __future__ import annotations

import streamlit as st

from operational_app.common import db_session, format_currency, safe_run, show_warning
from src.auth.permissions import has_permission
from src.crud import beneficios as crud_beneficios
from src.crud import colaboradores as crud_colaboradores
from src.crud import documentos as crud_documentos
from src.services.historico import listar_historico_colaborador
from src.services.masking import mask_cpf, mask_email, mask_phone


def _can_view_salary(profile: str) -> bool:
    return profile in {"admin", "dp", "financeiro", "rh"}


def render(user: dict):
    st.subheader("Colaboradores")
    filtros, cadastro = st.tabs(["Lista", "Novo colaborador"])

    with cadastro:
        with st.form("novo_colaborador"):
            nome = st.text_input("Nome completo")
            cpf = st.text_input("CPF")
            email = st.text_input("E-mail")
            telefone = st.text_input("Telefone")
            regime = st.selectbox("Regime contratual", ["CLT", "PJ", "Estagio", "Temporario"])
            status = st.selectbox("Status", ["pre_admissao", "ativo", "afastado", "ferias", "desligado", "inativo"])
            salario = st.text_input("Salario base", value="0,00")
            salvar = st.form_submit_button("Cadastrar colaborador")
        if salvar and nome:
            safe_run(
                lambda: _criar_colaborador(user, nome, cpf, email, telefone, regime, status, salario),
                success_message="Colaborador cadastrado.",
                error_prefix="Nao foi possivel cadastrar colaborador.",
            )

    with filtros:
        with db_session() as db:
            itens = crud_colaboradores.listar(db)
            vinculos = crud_beneficios.listar_vinculos(db)
            documentos = crud_documentos.listar(db)

        status_filtro = st.selectbox("Filtrar por status", ["Todos", "pre_admissao", "ativo", "afastado", "ferias", "desligado", "inativo"])
        if status_filtro != "Todos":
            itens = [item for item in itens if item.status == status_filtro]

        docs_por_colab = {}
        for item in documentos:
            docs_por_colab[item.colaborador_id] = docs_por_colab.get(item.colaborador_id, 0) + 1
        beneficios_por_colab = {}
        for item in vinculos:
            if item.status == "ativo":
                beneficios_por_colab[item.colaborador_id] = beneficios_por_colab.get(item.colaborador_id, 0) + 1

        st.dataframe(
            [
                {
                    "id": item.id,
                    "nome": item.nome_completo,
                    "cpf": mask_cpf(item.cpf),
                    "email": mask_email(item.email),
                    "telefone": mask_phone(item.telefone),
                    "status": item.status,
                    "salario": format_currency(item.salario_base) if _can_view_salary(user["perfil"]) else "Oculto",
                    "beneficios_ativos": beneficios_por_colab.get(item.id, 0),
                    "documentos": docs_por_colab.get(item.id, 0),
                }
                for item in itens
            ],
            use_container_width=True,
        )
        if not itens:
            show_warning("Nenhum colaborador encontrado para o filtro atual.")
            return

        selecionado = st.selectbox("Selecionar colaborador", [f"{item.id} - {item.nome_completo}" for item in itens])
        colaborador_id = int(selecionado.split(" - ")[0])
        historico_tab, detalhes_tab = st.tabs(["Historico funcional", "Detalhes"])
        with db_session() as db:
            colaborador = crud_colaboradores.buscar_por_id(db, colaborador_id)
            historico = listar_historico_colaborador(db, colaborador_id)
        with detalhes_tab:
            st.write(
                {
                    "nome": colaborador.nome_completo,
                    "status": colaborador.status,
                    "regime": colaborador.regime_contratual,
                    "cargo_id": colaborador.cargo_id,
                    "departamento_id": colaborador.departamento_id,
                    "centro_custo_id": colaborador.centro_custo_id,
                }
            )
        with historico_tab:
            st.dataframe(
                [
                    {
                        "data_evento": item.data_evento,
                        "tipo": item.tipo_evento,
                        "campo_alterado": item.campo_alterado,
                        "valor_anterior": "Oculto" if item.campo_alterado == "salario_base" and not _can_view_salary(user["perfil"]) else item.valor_anterior,
                        "valor_novo": "Oculto" if item.campo_alterado == "salario_base" and not _can_view_salary(user["perfil"]) else item.valor_novo,
                        "motivo": item.motivo,
                        "usuario_id": item.usuario_id,
                        "registrado_em": item.criado_em,
                    }
                    for item in historico
                ],
                use_container_width=True,
            )


def _criar_colaborador(user, nome, cpf, email, telefone, regime, status, salario):
    with db_session() as db:
        crud_colaboradores.criar(
            db,
            {
                "nome_completo": nome,
                "cpf": cpf,
                "email": email,
                "telefone": telefone,
                "regime_contratual": regime,
                "status": status,
                "salario_base": salario,
                "origem": "manual",
            },
            user["id"],
        )
