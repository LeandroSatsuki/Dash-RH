from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, update_record
from src.db.models import Colaborador, ColaboradorBeneficio, Desligamento
from src.services.audit_service import log_action
from src.services.historico import registrar_historico


def _validar_conclusao(colaborador: Colaborador, desligamento: Desligamento) -> None:
    if desligamento.data_desligamento is None:
        raise ValueError("Nao e possivel concluir desligamento sem data desligamento.")
    if desligamento.tipo_rescisao in (None, ""):
        raise ValueError("Nao e possivel concluir desligamento sem tipo de rescisao.")
    if colaborador.data_admissao and desligamento.data_desligamento < colaborador.data_admissao:
        raise ValueError("Data desligamento nao pode ser menor que admissao.")


def criar(db: Session, data: dict, usuario_id: int | None = None):
    payload = data.copy()
    payload.setdefault("status", "rascunho")
    return create_record(db, Desligamento, payload, usuario_id)


def listar(db: Session):
    return list_records(db, Desligamento, include_deleted=True)


def buscar_por_id(db: Session, desligamento_id: int):
    return get_record(db, Desligamento, desligamento_id)


def editar(db: Session, desligamento_id: int, data: dict, usuario_id: int | None = None):
    return update_record(db, buscar_por_id(db, desligamento_id), data, usuario_id)


def concluir(db: Session, desligamento_id: int, usuario_id: int | None = None):
    desligamento = buscar_por_id(db, desligamento_id)
    colaborador = db.get(Colaborador, desligamento.colaborador_id)
    if colaborador is None:
        raise ValueError("Colaborador nao encontrado.")
    _validar_conclusao(colaborador, desligamento)
    update_record(
        db,
        colaborador,
        {"status": "desligado", "data_desligamento": desligamento.data_desligamento},
        usuario_id,
    )
    for vinculo in db.query(ColaboradorBeneficio).filter(ColaboradorBeneficio.colaborador_id == colaborador.id, ColaboradorBeneficio.status == "ativo").all():
        update_record(db, vinculo, {"status": "encerrado", "data_fim": desligamento.data_desligamento}, usuario_id)
    updated = update_record(db, desligamento, {"status": "concluida"}, usuario_id)
    registrar_historico(
        db,
        colaborador_id=colaborador.id,
        tipo_evento="desligamento",
        data_evento=desligamento.data_desligamento,
        data_inicio=desligamento.data_aviso_previo,
        data_fim=desligamento.data_desligamento,
        usuario_id=usuario_id,
        motivo=desligamento.tipo_rescisao,
    )
    log_action(db, tabela="desligamentos", acao="concluir_desligamento", registro_id=updated.id, usuario_id=usuario_id, origem="desligamentos")
    return updated


def cancelar(db: Session, desligamento_id: int, usuario_id: int | None = None, motivo: str | None = None):
    desligamento = buscar_por_id(db, desligamento_id)
    updated = update_record(db, desligamento, {"status": "cancelada", "observacao": motivo or desligamento.observacao}, usuario_id)
    log_action(db, tabela="desligamentos", acao="cancelar_desligamento", registro_id=updated.id, usuario_id=usuario_id, origem="desligamentos")
    return updated
