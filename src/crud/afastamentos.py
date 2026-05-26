from __future__ import annotations

from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, soft_delete_record, update_record
from src.db.models import Afastamento
from src.services.validacoes_dp import validar_periodo


def _validar(data: dict) -> None:
    validar_periodo(data.get("data_inicio"), data.get("data_fim"), "Afastamento")


def criar(db: Session, data: dict, usuario_id: int | None = None):
    _validar(data)
    return create_record(db, Afastamento, data, usuario_id)


def listar(db: Session):
    return list_records(db, Afastamento)


def buscar_por_id(db: Session, afastamento_id: int):
    return get_record(db, Afastamento, afastamento_id)


def editar(db: Session, afastamento_id: int, data: dict, usuario_id: int | None = None):
    obj = buscar_por_id(db, afastamento_id)
    payload = {**obj.__dict__, **data}
    _validar(payload)
    return update_record(db, obj, data, usuario_id)


def remover(db: Session, afastamento_id: int, usuario_id: int | None = None):
    return soft_delete_record(db, buscar_por_id(db, afastamento_id), usuario_id)
