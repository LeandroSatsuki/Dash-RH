from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.crud import colaboradores as crud_colaboradores


def render(user: dict):
    st.subheader("Admissões")
    st.info("Use esta área para pré-admissão e conclusão manual de admissões. A base estrutural está pronta para evolução.")
    with db_session() as db:
        pre = [item for item in crud_colaboradores.listar(db) if item.status == "pre_admissao"]
        st.dataframe([{"id": item.id, "nome": item.nome_completo, "status": item.status, "origem": item.origem} for item in pre], use_container_width=True)
