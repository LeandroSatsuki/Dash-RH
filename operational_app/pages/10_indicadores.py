from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.services.indicadores import indicadores_dashboard


def render(user: dict):
    st.subheader("Indicadores")
    with db_session() as db:
        indicadores = indicadores_dashboard(db)
    cols = st.columns(4)
    for idx, (chave, valor) in enumerate(indicadores.items()):
        cols[idx % 4].metric(chave.replace("_", " ").title(), valor)
    st.json(indicadores)
