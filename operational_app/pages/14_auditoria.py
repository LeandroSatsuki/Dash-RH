from __future__ import annotations

from datetime import datetime, time

import pandas as pd
import streamlit as st

from operational_app.common import db_session
from src.services.audit_service import list_audit_logs


def render(user: dict):
    st.subheader("Auditoria")
    col1, col2, col3, col4, col5 = st.columns(5)
    usuario_id = col1.text_input("Usuário ID")
    tabela = col2.text_input("Tabela")
    acao = col3.text_input("Ação")
    registro_id = col4.text_input("Registro ID")
    data = col5.date_input("Data inicial", value=None)
    data_inicio = datetime.combine(data, time.min) if data else None
    with db_session() as db:
        itens = list_audit_logs(
            db,
            usuario_id=int(usuario_id) if usuario_id else None,
            tabela=tabela or None,
            acao=acao or None,
            registro_id=int(registro_id) if registro_id else None,
            data_inicio=data_inicio,
        )
    records = [
        {
            "id": item.id,
            "usuario_id": item.usuario_id,
            "tabela": item.tabela,
            "acao": item.acao,
            "registro_id": item.registro_id,
            "origem": item.origem,
            "criado_em": item.criado_em,
        }
        for item in itens
    ]
    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True)
    if not df.empty:
        st.download_button("Exportar CSV", data=df.to_csv(index=False), file_name="auditoria.csv", mime="text/csv")
