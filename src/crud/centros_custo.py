from __future__ import annotations

from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, soft_delete_record, update_record
from src.db.models import CentroCusto


def criar(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, CentroCusto, data, usuario_id)


def listar(db: Session):
    return list_records(db, CentroCusto)


def buscar_por_id(db: Session, centro_custo_id: int):
    return get_record(db, CentroCusto, centro_custo_id)


def editar(db: Session, centro_custo_id: int, data: dict, usuario_id: int | None = None):
    return update_record(db, buscar_por_id(db, centro_custo_id), data, usuario_id)


def remover(db: Session, centro_custo_id: int, usuario_id: int | None = None):
    return soft_delete_record(db, buscar_por_id(db, centro_custo_id), usuario_id)
