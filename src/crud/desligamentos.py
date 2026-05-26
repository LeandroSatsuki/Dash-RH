from __future__ import annotations

from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, update_record
from src.db.models import Colaborador, Desligamento


def criar(db: Session, data: dict, usuario_id: int | None = None):
    desligamento = create_record(db, Desligamento, data, usuario_id)
    colaborador = db.get(Colaborador, data["colaborador_id"])
    if colaborador is not None:
        colaborador.status = "desligado"
        colaborador.data_desligamento = data.get("data_desligamento")
        db.add(colaborador)
        db.commit()
    return desligamento


def listar(db: Session):
    return list_records(db, Desligamento, include_deleted=True)


def buscar_por_id(db: Session, desligamento_id: int):
    return get_record(db, Desligamento, desligamento_id)


def editar(db: Session, desligamento_id: int, data: dict, usuario_id: int | None = None):
    return update_record(db, buscar_por_id(db, desligamento_id), data, usuario_id)
