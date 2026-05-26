from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.crud import colaboradores as crud_colaboradores


def render(user: dict):
    st.subheader("Qualidade de dados")
    with db_session() as db:
        colaboradores = crud_colaboradores.listar(db)
    alertas = []
    for item in colaboradores:
        if item.regime_contratual == "CLT" and not item.cpf:
            alertas.append({"tipo": "CPF ausente", "colaborador": item.nome_completo})
        if item.status == "ativo" and item.data_desligamento is not None:
            alertas.append({"tipo": "Ativo com desligamento", "colaborador": item.nome_completo})
        if item.status == "desligado" and item.data_desligamento is None:
            alertas.append({"tipo": "Desligado sem data", "colaborador": item.nome_completo})
        if item.salario_base in (None, 0):
            alertas.append({"tipo": "Salário ausente", "colaborador": item.nome_completo})
        if item.cargo_id is None:
            alertas.append({"tipo": "Cargo ausente", "colaborador": item.nome_completo})
        if item.departamento_id is None:
            alertas.append({"tipo": "Departamento ausente", "colaborador": item.nome_completo})
    st.dataframe(alertas, use_container_width=True)
