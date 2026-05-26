from __future__ import annotations

from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, soft_delete_record, update_record
from src.db.models import Ferias
from src.services.validacoes_dp import validar_periodo


def _validar(data: dict) -> None:
    validar_periodo(data.get("data_inicio"), data.get("data_fim"), "Férias")


def criar(db: Session, data: dict, usuario_id: int | None = None):
    _validar(data)
    return create_record(db, Ferias, data, usuario_id)


def listar(db: Session):
    return list_records(db, Ferias)


def buscar_por_id(db: Session, ferias_id: int):
    return get_record(db, Ferias, ferias_id)


def editar(db: Session, ferias_id: int, data: dict, usuario_id: int | None = None):
    obj = buscar_por_id(db, ferias_id)
    payload = {**obj.__dict__, **data}
    _validar(payload)
    return update_record(db, obj, data, usuario_id)


def remover(db: Session, ferias_id: int, usuario_id: int | None = None):
    return soft_delete_record(db, buscar_por_id(db, ferias_id), usuario_id)
