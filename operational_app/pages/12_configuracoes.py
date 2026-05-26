from __future__ import annotations

from pathlib import Path

import streamlit as st

from operational_app.common import db_session
from src.services.importacao_excel import importar_arquivo_legado


def render(user: dict):
    st.subheader("Configurações e Importação")
    arquivo = st.file_uploader("Upload de planilha legada", type=["xlsx", "xlsm", "xls"])
    if arquivo is not None and st.button("Validar e importar planilha"):
        destino = Path("data/uploads") / arquivo.name
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_bytes(arquivo.getvalue())
        with db_session() as db:
            resultado = importar_arquivo_legado(db, destino, user["id"])
        st.success("Importação concluída.")
        st.json(resultado)
    st.info("Use `.env` para definir DATABASE_URL, SECRET_KEY e UPLOAD_DIR.")
