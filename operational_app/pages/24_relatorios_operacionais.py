from __future__ import annotations

import streamlit as st

from operational_app.common import db_session, safe_run
from src.services.report_service import build_operational_reports, export_report


def render(user: dict):
    st.subheader("Relatorios Operacionais")
    with db_session() as db:
        reports = build_operational_reports(db)
    nome = st.selectbox("Relatorio", list(reports.keys()))
    st.dataframe(reports[nome], use_container_width=True)
    col1, col2 = st.columns(2)
    if col1.button("Exportar CSV"):
        with db_session() as db:
            content = export_report(db, report_name=nome, formato="csv", usuario_id=user["id"])
        st.download_button("Baixar CSV", content, file_name=f"{nome}.csv", mime="text/csv")
    if col2.button("Exportar XLSX"):
        with db_session() as db:
            content = export_report(db, report_name=nome, formato="xlsx", usuario_id=user["id"])
        st.download_button("Baixar XLSX", content, file_name=f"{nome}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
