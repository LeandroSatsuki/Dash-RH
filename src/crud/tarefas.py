from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud.base import create_record, list_records, soft_delete_record, update_record
from src.db.models import Documento, Tarefa, TarefaAnexo, TarefaComentario


def criar(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, Tarefa, data, usuario_id)


def listar(
    db: Session,
    *,
    responsavel_id: int | None = None,
    status: str | None = None,
    prioridade: str | None = None,
    modulo: str | None = None,
):
    stmt = select(Tarefa).where(Tarefa.deletado_em.is_(None))
    if responsavel_id is not None:
        stmt = stmt.where(Tarefa.responsavel_id == responsavel_id)
    if status:
        stmt = stmt.where(Tarefa.status == status)
    if prioridade:
        stmt = stmt.where(Tarefa.prioridade == prioridade)
    if modulo:
        stmt = stmt.where(Tarefa.modulo == modulo)
    stmt = stmt.order_by(Tarefa.criado_em.desc())
    return list(db.scalars(stmt).all())


def buscar_por_id(db: Session, tarefa_id: int):
    return db.get(Tarefa, tarefa_id)


def editar(db: Session, tarefa_id: int, data: dict, usuario_id: int | None = None):
    return update_record(db, buscar_por_id(db, tarefa_id), data, usuario_id)


def concluir(db: Session, tarefa_id: int, usuario_id: int | None = None):
    return editar(
        db,
        tarefa_id,
        {"status": "concluida", "concluido_em": datetime.now(UTC).replace(tzinfo=None)},
        usuario_id,
    )


def cancelar(db: Session, tarefa_id: int, motivo: str, usuario_id: int | None = None):
    return editar(db, tarefa_id, {"status": "cancelada", "motivo_cancelamento": motivo}, usuario_id)


def remover(db: Session, tarefa_id: int, usuario_id: int | None = None):
    return soft_delete_record(db, buscar_por_id(db, tarefa_id), usuario_id)


def criar_comentario(db: Session, tarefa_id: int, comentario: str, usuario_id: int | None = None):
    return create_record(db, TarefaComentario, {"tarefa_id": tarefa_id, "comentario": comentario, "usuario_id": usuario_id}, usuario_id)


def listar_comentarios(db: Session, tarefa_id: int):
    stmt = select(TarefaComentario).where(TarefaComentario.tarefa_id == tarefa_id).order_by(TarefaComentario.criado_em.asc())
    return list(db.scalars(stmt).all())


def anexar_documento(db: Session, tarefa_id: int, documento_id: int, usuario_id: int | None = None):
    documento = db.get(Documento, documento_id)
    if documento is None:
        raise ValueError("Documento nao encontrado.")
    return create_record(db, TarefaAnexo, {"tarefa_id": tarefa_id, "documento_id": documento_id}, usuario_id)


def listar_anexos(db: Session, tarefa_id: int):
    stmt = select(TarefaAnexo).where(TarefaAnexo.tarefa_id == tarefa_id)
    return list(db.scalars(stmt).all())
