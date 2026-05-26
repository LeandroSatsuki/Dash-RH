from __future__ import annotations

import pandas as pd
import streamlit as st

from operational_app.common import db_session
from src.services.calendar_service import build_calendar_events


def render(user: dict):
    st.subheader("Calendario Operacional")
    with db_session() as db:
        eventos = build_calendar_events(db)
    tipo = st.selectbox("Tipo de evento", ["Todos"] + sorted({item["tipo"] for item in eventos}))
    if tipo != "Todos":
        eventos = [item for item in eventos if item["tipo"] == tipo]
    st.dataframe(pd.DataFrame(eventos), use_container_width=True)
