from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud.base import create_record, list_records, update_record
from src.db.models import Colaborador, Documento, DocumentoObrigatorioRegra, DocumentoPendencia, TipoDocumento
from src.services.audit_service import log_action


def criar_tipo_documento(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, TipoDocumento, data, usuario_id)


def listar_tipos_documento(db: Session):
    return list_records(db, TipoDocumento, include_deleted=True)


def criar_regra(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, DocumentoObrigatorioRegra, data, usuario_id)


def listar_regras(db: Session):
    return list_records(db, DocumentoObrigatorioRegra, include_deleted=True)


def _regra_aplica(colaborador: Colaborador, regra: DocumentoObrigatorioRegra) -> bool:
    if regra.regime_contratual and regra.regime_contratual != colaborador.regime_contratual:
        return False
    if regra.cargo_id and regra.cargo_id != colaborador.cargo_id:
        return False
    if regra.departamento_id and regra.departamento_id != colaborador.departamento_id:
        return False
    return regra.obrigatorio


def gerar_pendencias(db: Session, usuario_id: int | None = None):
    regras = listar_regras(db)
    tipos = {item.id: item for item in listar_tipos_documento(db)}
    documentos = list_records(db, Documento)
    pendencias_geradas = []
    for colaborador in db.scalars(select(Colaborador).where(Colaborador.deletado_em.is_(None))).all():
        for regra in regras:
            if not _regra_aplica(colaborador, regra):
                continue
            tipo = tipos.get(regra.tipo_documento_id)
            doc = next((item for item in documentos if item.colaborador_id == colaborador.id and item.tipo_documento == tipo.nome), None) if tipo else None
            existente = db.scalar(
                select(DocumentoPendencia).where(
                    DocumentoPendencia.colaborador_id == colaborador.id,
                    DocumentoPendencia.tipo_documento_id == regra.tipo_documento_id,
                    DocumentoPendencia.status.in_(["pendente", "enviado", "vencido"]),
                )
            )
            if doc is None and existente is None:
                data_vencimento = date.today() + timedelta(days=regra.validade_dias or 0) if regra.validade_dias else None
                pendencias_geradas.append(
                    create_record(
                        db,
                        DocumentoPendencia,
                        {
                            "colaborador_id": colaborador.id,
                            "tipo_documento_id": regra.tipo_documento_id,
                            "status": "pendente",
                            "data_vencimento": data_vencimento,
                            "severidade": "alta" if tipo and tipo.sensivel else "media",
                        },
                        usuario_id,
                    )
                )
            elif doc is not None and existente is not None and doc.validade and doc.validade < date.today():
                update_record(db, existente, {"status": "vencido", "data_vencimento": doc.validade}, usuario_id)
    log_action(db, tabela="documentos_pendencias", acao="gerar_pendencias_documentos", usuario_id=usuario_id, origem="documentos_obrigatorios")
    return pendencias_geradas


def listar_pendencias(db: Session):
    return list_records(db, DocumentoPendencia, include_deleted=True)


def aprovar_pendencia(db: Session, pendencia_id: int, usuario_id: int | None = None):
    pendencia = db.get(DocumentoPendencia, pendencia_id)
    return update_record(db, pendencia, {"status": "aprovado", "resolvido_em": datetime.now(UTC).replace(tzinfo=None)}, usuario_id)


def dispensar_pendencia(db: Session, pendencia_id: int, justificativa: str, usuario_id: int | None = None):
    if not justificativa:
        raise ValueError("Dispensa de documento exige justificativa.")
    pendencia = db.get(DocumentoPendencia, pendencia_id)
    updated = update_record(
        db,
        pendencia,
        {"status": "dispensado", "justificativa": justificativa, "resolvido_em": datetime.now(UTC).replace(tzinfo=None)},
        usuario_id,
    )
    from src.services import workflow_service

    workflow_service.request_approval_for_entity(
        db,
        modulo="documentos",
        entidade_tipo="documento_pendencia_dispensa",
        entidade_id=pendencia_id,
        solicitante_id=usuario_id,
        comentario=justificativa,
    )
    return updated
