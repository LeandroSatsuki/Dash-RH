from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.crud.base import create_record, list_records, update_record
from src.db.models import ColaboradorTreinamentoSST, EPI, EntregaEPI, ExameOcupacional, TreinamentoSST
from src.services.audit_service import log_action


def criar_exame(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, ExameOcupacional, data, usuario_id)


def listar_exames(db: Session):
    return list_records(db, ExameOcupacional, include_deleted=True)


def criar_epi(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, EPI, data, usuario_id)


def listar_epis(db: Session):
    return list_records(db, EPI, include_deleted=True)


def criar_entrega_epi(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, EntregaEPI, data, usuario_id)


def listar_entregas_epi(db: Session):
    return list_records(db, EntregaEPI, include_deleted=True)


def criar_treinamento(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, TreinamentoSST, data, usuario_id)


def listar_treinamentos(db: Session):
    return list_records(db, TreinamentoSST, include_deleted=True)


def vincular_treinamento(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, ColaboradorTreinamentoSST, data, usuario_id)


def listar_colaborador_treinamentos(db: Session):
    return list_records(db, ColaboradorTreinamentoSST, include_deleted=True)
