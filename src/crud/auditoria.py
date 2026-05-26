from __future__ import annotations

from sqlalchemy.orm import Session

from src.services.audit_service import list_audit_logs


def listar(db: Session, **filters):
    return list_audit_logs(db, **filters)
