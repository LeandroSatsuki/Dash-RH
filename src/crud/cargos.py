from __future__ import annotations

from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, soft_delete_record, update_record
from src.db.models import Cargo


def criar(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, Cargo, data, usuario_id)


def listar(db: Session):
    return list_records(db, Cargo)


def buscar_por_id(db: Session, cargo_id: int):
    return get_record(db, Cargo, cargo_id)


def editar(db: Session, cargo_id: int, data: dict, usuario_id: int | None = None):
    return update_record(db, buscar_por_id(db, cargo_id), data, usuario_id)


def remover(db: Session, cargo_id: int, usuario_id: int | None = None):
    return soft_delete_record(db, buscar_por_id(db, cargo_id), usuario_id)
