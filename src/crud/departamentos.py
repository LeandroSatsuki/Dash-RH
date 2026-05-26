from __future__ import annotations

from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, soft_delete_record, update_record
from src.db.models import Departamento


def criar(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, Departamento, data, usuario_id)


def listar(db: Session):
    return list_records(db, Departamento)


def buscar_por_id(db: Session, departamento_id: int):
    return get_record(db, Departamento, departamento_id)


def editar(db: Session, departamento_id: int, data: dict, usuario_id: int | None = None):
    obj = buscar_por_id(db, departamento_id)
    return update_record(db, obj, data, usuario_id)


def remover(db: Session, departamento_id: int, usuario_id: int | None = None):
    obj = buscar_por_id(db, departamento_id)
    return soft_delete_record(db, obj, usuario_id)
