from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud.base import create_record, list_records, update_record
from src.db.models import Notificacao


def criar(db: Session, data: dict, usuario_id: int | None = None):
    payload = data.copy()
    payload.setdefault("lida", False)
    return create_record(db, Notificacao, payload, usuario_id)


def listar(db: Session, usuario_id: int | None = None, apenas_nao_lidas: bool = False):
    stmt = select(Notificacao)
    if usuario_id is not None:
        stmt = stmt.where(Notificacao.usuario_id == usuario_id)
    if apenas_nao_lidas:
        stmt = stmt.where(Notificacao.lida.is_(False))
    stmt = stmt.order_by(Notificacao.criado_em.desc())
    return list(db.scalars(stmt).all())


def marcar_lida(db: Session, notificacao_id: int, usuario_id: int | None = None):
    notificacao = db.get(Notificacao, notificacao_id)
    if notificacao is None:
        raise ValueError("Notificacao nao encontrada.")
    return update_record(
        db,
        notificacao,
        {"lida": True, "lida_em": datetime.now(UTC).replace(tzinfo=None)},
        usuario_id,
    )


def marcar_todas_lidas(db: Session, usuario_id: int):
    notificacoes = listar(db, usuario_id=usuario_id, apenas_nao_lidas=True)
    for notificacao in notificacoes:
        notificacao.lida = True
        notificacao.lida_em = datetime.now(UTC).replace(tzinfo=None)
        db.add(notificacao)
    db.commit()
    return len(notificacoes)
