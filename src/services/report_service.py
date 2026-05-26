from __future__ import annotations

from io import BytesIO

import pandas as pd
from sqlalchemy.orm import Session

from src.crud import tarefas as crud_tarefas
from src.db.models import Alerta, DocumentoPendencia, ExameOcupacional, Ferias
from src.services.audit_service import log_action
from src.services.masking import mask_cpf


def build_operational_reports(db: Session) -> dict[str, list[dict]]:
    return {
        "tarefas_abertas": [{"id": item.id, "titulo": item.titulo, "status": item.status, "prioridade": item.prioridade, "responsavel_id": item.responsavel_id} for item in crud_tarefas.listar(db) if item.status not in {"concluida", "cancelada"}],
        "aprovacoes_pendentes": [],
        "ferias_pendentes_aprovacao": [{"id": item.id, "colaborador_id": item.colaborador_id, "status": item.status} for item in db.query(Ferias).filter(Ferias.status.in_(["planejada", "solicitada"])).all()],
        "documentos_vencidos": [{"id": item.id, "colaborador_id": item.colaborador_id, "status": item.status} for item in db.query(DocumentoPendencia).filter(DocumentoPendencia.status == "vencido").all()],
        "exames_vencidos": [{"id": item.id, "colaborador_id": item.colaborador_id, "tipo_exame": item.tipo_exame} for item in db.query(ExameOcupacional).all() if item.data_validade and item.data_validade < pd.Timestamp.now().date()],
        "alertas_criticos": [{"id": item.id, "tipo": item.tipo, "titulo": item.titulo} for item in db.query(Alerta).filter(Alerta.severidade == "critica", Alerta.status == "aberto").all()],
    }


def export_report(db: Session, *, report_name: str, formato: str, usuario_id: int | None = None) -> bytes:
    reports = build_operational_reports(db)
    if report_name not in reports:
        raise ValueError("Relatorio operacional nao encontrado.")
    df = pd.DataFrame(reports[report_name])
    buffer = BytesIO()
    if formato == "csv":
        buffer.write(df.to_csv(index=False).encode("utf-8"))
    elif formato == "xlsx":
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
    else:
        raise ValueError("Formato de exportacao invalido.")
    log_action(db, tabela="relatorios_operacionais", acao="exportar_relatorio", usuario_id=usuario_id, origem="relatorios", valor_novo={"report_name": report_name, "formato": formato})
    return buffer.getvalue()
