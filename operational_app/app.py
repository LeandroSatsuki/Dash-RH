from __future__ import annotations

import importlib.util
from pathlib import Path

import streamlit as st

from operational_app.auth import can_access, require_streamlit_login


PAGES = {
    "Home": {"file": None, "permission": "indicadores:view"},
    "Cadastros": {"file": "01_cadastros.py", "permission": "beneficios:create"},
    "Colaboradores": {"file": "02_colaboradores.py", "permission": "colaboradores:view"},
    "Admissoes": {"file": "03_admissoes.py", "permission": "admissoes:view"},
    "Ferias": {"file": "04_ferias.py", "permission": "ferias:view"},
    "Afastamentos": {"file": "05_afastamentos.py", "permission": "afastamentos:view"},
    "Beneficios": {"file": "06_beneficios.py", "permission": "beneficios:view"},
    "Folha": {"file": "07_folha.py", "permission": "folha:view"},
    "Desligamentos": {"file": "08_desligamentos.py", "permission": "desligamentos:view"},
    "Documentos": {"file": "09_documentos.py", "permission": "documentos:view"},
    "Indicadores": {"file": "10_indicadores.py", "permission": "indicadores:view"},
    "Qualidade de dados": {"file": "11_qualidade_dados.py", "permission": "indicadores:view"},
    "Configuracoes": {"file": "12_configuracoes.py", "permission": "documentos:create"},
    "Qualidade Operacional": {"file": "13_qualidade_operacional.py", "permission": "qualidade:view"},
    "Auditoria": {"file": "14_auditoria.py", "permission": "auditoria:view"},
    "Jornadas": {"file": "15_jornadas.py", "permission": "jornadas:view"},
    "Ponto": {"file": "16_ponto.py", "permission": "ponto:view"},
    "Banco de Horas": {"file": "17_banco_horas.py", "permission": "banco_horas:view"},
    "Documentos Obrigatorios": {"file": "18_documentos_obrigatorios.py", "permission": "documentos_obrigatorios:view"},
    "SST": {"file": "19_sst.py", "permission": "sst:view"},
    "Alertas": {"file": "20_alertas.py", "permission": "alertas:view"},
}


def load_page_module(filename: str):
    pages_dir = Path(__file__).parent / "pages"
    target = pages_dir / filename
    module_name = f"operational_page_{target.stem}"
    spec = importlib.util.spec_from_file_location(module_name, target)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def render_home(user: dict):
    from sqlalchemy import func, select

    from operational_app.common import db_session
    from src.db.models import CompetenciaFolha, DocumentoPendencia, ExameOcupacional
    from src.services import alerts
    from src.services.data_quality import generate_operational_quality_report
    from src.services.indicadores import indicadores_dashboard, indicadores_operacionais

    st.subheader("Home")
    with db_session() as db:
        alerts.gerar_alertas(db)
        indicadores = indicadores_dashboard(db)
        operacionais = indicadores_operacionais(db)
        quality_issues = generate_operational_quality_report(db)
        competencias_abertas = db.scalar(
            select(func.count())
            .select_from(CompetenciaFolha)
            .where(CompetenciaFolha.status.in_(["aberta", "reaberta", "em_conferencia"]))
        ) or 0
        documentos_pendentes = db.scalar(select(func.count()).select_from(DocumentoPendencia).where(DocumentoPendencia.status == "pendente")) or 0
        exames_vencidos = db.scalar(select(func.count()).select_from(ExameOcupacional).where(ExameOcupacional.data_validade.is_not(None), ExameOcupacional.data_validade < func.current_date())) or 0

    cards = [
        ("Colaboradores ativos", indicadores["headcount_ativo"]),
        ("Admissoes pendentes", indicadores["admissoes"]),
        ("Ferias a vencer", operacionais["kpis"]["ferias_a_vencer"]),
        ("Afastados", operacionais["kpis"]["afastados_ativos"]),
        ("Documentos pendentes", documentos_pendentes),
        ("Exames vencidos", exames_vencidos),
        ("Ponto inconsistente", int(operacionais["kpis"]["taxa_inconsistencia_ponto"] * 100)),
        ("Competencias abertas", competencias_abertas),
        ("Problemas criticos", len([item for item in quality_issues if item["severidade"] == "critica"])),
        ("Alertas criticos", indicadores["alertas_criticos"]),
    ]
    cols = st.columns(3)
    for idx, (label, value) in enumerate(cards):
        cols[idx % 3].metric(label, value)
    st.markdown("**Pendencias operacionais**")
    st.dataframe(quality_issues[:20], use_container_width=True)


def main():
    st.set_page_config(page_title="Dash-RH Operacional", layout="wide")
    st.title("Dash-RH Operacional")
    user = require_streamlit_login()
    if not user:
        st.info("Entre com um usuario valido para acessar o mini ERP.")
        return
    allowed_pages = [name for name, config in PAGES.items() if can_access(config["permission"])]
    page = st.sidebar.radio("Navegacao", allowed_pages)
    if page == "Home":
        render_home(user)
        return
    try:
        module = load_page_module(PAGES[page]["file"])
        module.render(user)
    except Exception:
        st.error("Nao foi possivel carregar a pagina solicitada.")


if __name__ == "__main__":
    main()
