from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.crud import beneficios as crud_beneficios
from src.crud import colaboradores as crud_colaboradores
from src.crud import documentos as crud_documentos
from src.services.masking import mask_cpf, mask_email, mask_phone


def render(user: dict):
    st.subheader("Colaboradores")
    with st.form("novo_colaborador"):
        nome = st.text_input("Nome completo")
        cpf = st.text_input("CPF")
        email = st.text_input("E-mail")
        telefone = st.text_input("Telefone")
        regime = st.selectbox("Regime contratual", ["CLT", "PJ", "Estágio", "Temporário"])
        status = st.selectbox("Status", ["pre_admissao", "ativo", "afastado", "ferias", "desligado", "inativo"])
        salario = st.number_input("Salário base", min_value=0.0, value=0.0, step=100.0)
        salvar = st.form_submit_button("Cadastrar colaborador")
    if salvar and nome:
        with db_session() as db:
            crud_colaboradores.criar(
                db,
                {"nome_completo": nome, "cpf": cpf, "email": email, "telefone": telefone, "regime_contratual": regime, "status": status, "salario_base": salario, "origem": "manual"},
                user["id"],
            )
        st.success("Colaborador cadastrado.")
    with db_session() as db:
        itens = crud_colaboradores.listar(db)
        st.dataframe(
            [{"id": item.id, "nome": item.nome_completo, "cpf": mask_cpf(item.cpf), "email": mask_email(item.email), "telefone": mask_phone(item.telefone), "status": item.status, "salario": item.salario_base} for item in itens],
            use_container_width=True,
        )
