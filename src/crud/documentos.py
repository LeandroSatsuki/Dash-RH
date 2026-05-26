from __future__ import annotations

from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, soft_delete_record, update_record
from src.db.models import Documento
from src.services.file_storage import ensure_within_upload_dir


def criar(db: Session, data: dict, usuario_id: int | None = None):
    ensure_within_upload_dir(data["caminho_arquivo"])
    return create_record(db, Documento, data, usuario_id)


def listar(db: Session):
    return list_records(db, Documento)


def buscar_por_id(db: Session, documento_id: int):
    return get_record(db, Documento, documento_id)


def editar(db: Session, documento_id: int, data: dict, usuario_id: int | None = None):
    if "caminho_arquivo" in data:
        ensure_within_upload_dir(data["caminho_arquivo"])
    return update_record(db, buscar_por_id(db, documento_id), data, usuario_id)


def remover(db: Session, documento_id: int, usuario_id: int | None = None):
    return soft_delete_record(db, buscar_por_id(db, documento_id), usuario_id)
