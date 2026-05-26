from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.services.audit_service import compare_changes, log_action


def create_record(db: Session, model, data: dict[str, Any], usuario_id: int | None = None):
    obj = model(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    log_action(db, tabela=model.__tablename__, acao="create", registro_id=obj.id, usuario_id=usuario_id, valor_novo=data, origem="crud")
    return obj


def list_records(db: Session, model, include_deleted: bool = False):
    stmt = select(model)
    if hasattr(model, "deletado_em") and not include_deleted:
        stmt = stmt.where(model.deletado_em.is_(None))
    return list(db.scalars(stmt).all())


def get_record(db: Session, model, record_id: int):
    return db.get(model, record_id)


def update_record(db: Session, obj, data: dict[str, Any], usuario_id: int | None = None):
    before = {key: getattr(obj, key) for key in data.keys()}
    for key, value in data.items():
        setattr(obj, key, value)
    if hasattr(obj, "atualizado_em"):
        obj.atualizado_em = datetime.now(UTC).replace(tzinfo=None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    changes = compare_changes(before, data)
    log_action(
        db,
        tabela=obj.__tablename__,
        acao="update",
        registro_id=obj.id,
        usuario_id=usuario_id,
        valor_anterior=before,
        valor_novo=data,
        campo_alterado=", ".join(change["campo"] for change in changes) if changes else None,
        origem="crud",
    )
    return obj


def soft_delete_record(db: Session, obj, usuario_id: int | None = None):
    if hasattr(obj, "deletado_em"):
        obj.deletado_em = datetime.now(UTC).replace(tzinfo=None)
    if hasattr(obj, "status"):
        try:
            obj.status = "inativo"
        except Exception:
            pass
    db.add(obj)
    db.commit()
    log_action(db, tabela=obj.__tablename__, acao="soft_delete", registro_id=obj.id, usuario_id=usuario_id, origem="crud")
    return obj
