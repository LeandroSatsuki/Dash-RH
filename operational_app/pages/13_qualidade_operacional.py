from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.services.data_quality import generate_operational_quality_report


def render(user: dict):
    st.subheader("Qualidade Operacional")
    with db_session() as db:
        issues = generate_operational_quality_report(db)
    severities = ["baixa", "média", "alta", "crítica"]
    cols = st.columns(4)
    for idx, severity in enumerate(severities):
        cols[idx].metric(severity.title(), len([item for item in issues if item["severidade"] == severity]))
    st.dataframe(issues, use_container_width=True)
