from datetime import UTC, datetime

from src.services.report_service import build_operational_reports, export_report
from src.services.task_service import create_task


def test_relatorios_operacionais_geram_dados(db):
    create_task(db, {"titulo": "Relatorio", "modulo": "geral", "responsavel_id": 1, "prazo": datetime.now(UTC).replace(tzinfo=None)}, 1)
    reports = build_operational_reports(db)
    assert "tarefas_abertas" in reports
    assert len(reports["tarefas_abertas"]) == 1


def test_exportacao_csv_retorna_bytes(db):
    create_task(db, {"titulo": "Exportar", "modulo": "geral", "responsavel_id": 1, "prazo": datetime.now(UTC).replace(tzinfo=None)}, 1)
    content = export_report(db, report_name="tarefas_abertas", formato="csv", usuario_id=1)
    assert isinstance(content, bytes)
    assert b"titulo" in content


def test_exportacao_xlsx_retorna_bytes(db):
    create_task(db, {"titulo": "Exportar XLSX", "modulo": "geral", "responsavel_id": 1, "prazo": datetime.now(UTC).replace(tzinfo=None)}, 1)
    content = export_report(db, report_name="tarefas_abertas", formato="xlsx", usuario_id=1)
    assert isinstance(content, bytes)
    assert len(content) > 10
