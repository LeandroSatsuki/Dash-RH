from __future__ import annotations

from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, soft_delete_record, update_record
from src.db.models import Beneficio, ColaboradorBeneficio


def criar(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, Beneficio, data, usuario_id)


def listar(db: Session):
    return list_records(db, Beneficio, include_deleted=True)


def buscar_por_id(db: Session, beneficio_id: int):
    return get_record(db, Beneficio, beneficio_id)


def editar(db: Session, beneficio_id: int, data: dict, usuario_id: int | None = None):
    return update_record(db, buscar_por_id(db, beneficio_id), data, usuario_id)


def remover(db: Session, beneficio_id: int, usuario_id: int | None = None):
    obj = buscar_por_id(db, beneficio_id)
    obj.status = "inativo"
    return update_record(db, obj, {"status": "inativo"}, usuario_id)


def vincular_ao_colaborador(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, ColaboradorBeneficio, data, usuario_id)


def listar_vinculos(db: Session):
    return list_records(db, ColaboradorBeneficio, include_deleted=True)
