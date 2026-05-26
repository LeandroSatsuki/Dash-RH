from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, soft_delete_record, update_record
from src.db.models import CompetenciaFolha, FolhaSnapshot, LancamentoFolha, Rubrica
from src.services.audit_service import log_action
from src.services.validacoes_dp import validar_valor_lancamento
from src.utils.money import safe_decimal


def criar_competencia(db: Session, data: dict, usuario_id: int | None = None):
    existente = db.scalar(
        select(CompetenciaFolha).where(
            CompetenciaFolha.ano == data["ano"],
            CompetenciaFolha.mes == data["mes"],
            CompetenciaFolha.status.in_(["aberta", "em_conferencia", "reaberta"]),
        )
    )
    if existente is not None:
        raise ValueError("Não pode haver duas competências abertas para o mesmo mês/ano.")
    if not data.get("data_abertura"):
        data["data_abertura"] = datetime.now(UTC).replace(tzinfo=None)
    return create_record(db, CompetenciaFolha, data, usuario_id)


def listar_competencias(db: Session):
    return list_records(db, CompetenciaFolha, include_deleted=True)


def buscar_competencia(db: Session, competencia_id: int):
    return get_record(db, CompetenciaFolha, competencia_id)


def editar_competencia(db: Session, competencia_id: int, data: dict, usuario_id: int | None = None):
    return update_record(db, buscar_competencia(db, competencia_id), data, usuario_id)


def _build_snapshot(db: Session, competencia_id: int, usuario_id: int | None = None) -> FolhaSnapshot:
    lancamentos = db.scalars(select(LancamentoFolha).where(LancamentoFolha.competencia_id == competencia_id, LancamentoFolha.deletado_em.is_(None))).all()
    total_proventos = sum((item.valor for item in lancamentos if item.tipo == "provento"), Decimal("0"))
    total_descontos = sum((item.valor for item in lancamentos if item.tipo == "desconto"), Decimal("0"))
    total_encargos = sum((item.valor for item in lancamentos if item.tipo == "encargo"), Decimal("0"))
    total_beneficios = sum((item.valor for item in lancamentos if item.tipo == "beneficio"), Decimal("0"))
    total_liquido_estimado = total_proventos - total_descontos
    total_custo_empresa = total_proventos + total_encargos + total_beneficios
    quantidade_colaboradores = len({item.colaborador_id for item in lancamentos})
    snapshot = db.scalar(select(FolhaSnapshot).where(FolhaSnapshot.competencia_id == competencia_id))
    payload = {
        "competencia_id": competencia_id,
        "total_proventos": total_proventos,
        "total_descontos": total_descontos,
        "total_encargos": total_encargos,
        "total_beneficios": total_beneficios,
        "total_liquido_estimado": total_liquido_estimado,
        "total_custo_empresa": total_custo_empresa,
        "quantidade_colaboradores": quantidade_colaboradores,
        "usuario_id": usuario_id,
    }
    if snapshot is None:
        snapshot = FolhaSnapshot(**payload)
        db.add(snapshot)
    else:
        for key, value in payload.items():
            setattr(snapshot, key, value)
        db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def fechar_competencia(db: Session, competencia_id: int, usuario_id: int | None = None):
    competencia = buscar_competencia(db, competencia_id)
    updated = update_record(
        db,
        competencia,
        {"status": "fechada", "data_fechamento": datetime.now(UTC).replace(tzinfo=None), "usuario_fechamento_id": usuario_id},
        usuario_id,
    )
    snapshot = _build_snapshot(db, competencia_id, usuario_id)
    log_action(db, tabela="competencias_folha", acao="fechar_competencia", registro_id=updated.id, usuario_id=usuario_id, origem="folha", valor_novo={"competencia": updated.competencia, "snapshot_id": snapshot.id})
    return updated


def reabrir_competencia(db: Session, competencia_id: int, usuario_id: int | None = None):
    updated = update_record(db, buscar_competencia(db, competencia_id), {"status": "reaberta"}, usuario_id)
    log_action(db, tabela="competencias_folha", acao="reabrir_competencia", registro_id=updated.id, usuario_id=usuario_id, origem="folha", valor_novo={"competencia": updated.competencia})
    return updated


def criar_rubrica(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, Rubrica, data, usuario_id)


def listar_rubricas(db: Session):
    return list_records(db, Rubrica, include_deleted=True)


def buscar_rubrica(db: Session, rubrica_id: int):
    return get_record(db, Rubrica, rubrica_id)


def editar_rubrica(db: Session, rubrica_id: int, data: dict, usuario_id: int | None = None):
    return update_record(db, buscar_rubrica(db, rubrica_id), data, usuario_id)


def criar_lancamento(db: Session, data: dict, usuario_id: int | None = None):
    competencia = buscar_competencia(db, data["competencia_id"])
    if competencia.status == "fechada":
        raise ValueError("Competência fechada não pode receber novos lançamentos sem reabertura.")
    rubrica = buscar_rubrica(db, data["rubrica_id"])
    valor = safe_decimal(data["valor"])
    validar_valor_lancamento(float(valor or 0), getattr(rubrica, "tipo", None))
    payload = {**data, "valor": valor}
    return create_record(db, LancamentoFolha, payload, usuario_id)


def listar_lancamentos(db: Session):
    return list_records(db, LancamentoFolha)


def buscar_lancamento(db: Session, lancamento_id: int):
    return get_record(db, LancamentoFolha, lancamento_id)


def editar_lancamento(db: Session, lancamento_id: int, data: dict, usuario_id: int | None = None):
    obj = buscar_lancamento(db, lancamento_id)
    competencia = buscar_competencia(db, obj.competencia_id)
    if competencia.status == "fechada":
        raise ValueError("Competência fechada não pode ser alterada sem reabertura.")
    rubrica = buscar_rubrica(db, data.get("rubrica_id", obj.rubrica_id))
    payload = data.copy()
    if "valor" in payload and payload["valor"] is not None:
        payload["valor"] = safe_decimal(payload["valor"])
        validar_valor_lancamento(float(payload["valor"] or 0), getattr(rubrica, "tipo", None))
    return update_record(db, obj, payload, usuario_id)


def remover_lancamento(db: Session, lancamento_id: int, usuario_id: int | None = None):
    obj = buscar_lancamento(db, lancamento_id)
    competencia = buscar_competencia(db, obj.competencia_id)
    if competencia.status == "fechada":
        raise ValueError("Competência fechada não pode ser alterada sem reabertura.")
    return soft_delete_record(db, obj, usuario_id)


def buscar_snapshot(db: Session, competencia_id: int):
    return db.scalar(select(FolhaSnapshot).where(FolhaSnapshot.competencia_id == competencia_id))


def resumo_competencia(db: Session, competencia_id: int) -> dict:
    competencia = buscar_competencia(db, competencia_id)
    snapshot = buscar_snapshot(db, competencia_id)
    if snapshot is None:
        snapshot = _build_snapshot(db, competencia_id)
    return {
        "competencia_id": competencia.id,
        "competencia": competencia.competencia,
        "status": competencia.status,
        "total_proventos": float(snapshot.total_proventos or 0),
        "total_descontos": float(snapshot.total_descontos or 0),
        "total_encargos": float(snapshot.total_encargos or 0),
        "total_beneficios": float(snapshot.total_beneficios or 0),
        "total_liquido_estimado": float(snapshot.total_liquido_estimado or 0),
        "total_custo_empresa": float(snapshot.total_custo_empresa or 0),
        "quantidade_colaboradores": int(snapshot.quantidade_colaboradores or 0),
    }


def exportar_competencia(db: Session, competencia_id: int) -> list[dict]:
    rows = db.execute(
        select(LancamentoFolha, Rubrica)
        .join(Rubrica, Rubrica.id == LancamentoFolha.rubrica_id)
        .where(LancamentoFolha.competencia_id == competencia_id, LancamentoFolha.deletado_em.is_(None))
    ).all()
    export = []
    for lancamento, rubrica in rows:
        export.append(
            {
                "competencia_id": lancamento.competencia_id,
                "colaborador_id": lancamento.colaborador_id,
                "rubrica_codigo": rubrica.codigo,
                "rubrica_descricao": rubrica.descricao,
                "tipo": lancamento.tipo,
                "valor": float(lancamento.valor or 0),
                "quantidade": lancamento.quantidade,
                "origem": lancamento.origem,
            }
        )
    return export
