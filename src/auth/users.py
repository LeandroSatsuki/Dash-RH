from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth.security import verify_password
from src.db.models import Usuario
from src.services.audit_service import log_action


def get_user_by_email(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.email == email))


def authenticate_user(db: Session, email: str, password: str) -> Usuario | None:
    user = get_user_by_email(db, email)
    if not user or not user.ativo:
        log_action(db, tabela="usuarios", acao="login_failed", origem="auth", valor_novo={"email": email})
        return None
    if not verify_password(password, user.senha_hash):
        log_action(db, tabela="usuarios", acao="login_failed", registro_id=user.id, usuario_id=user.id, origem="auth", valor_novo={"email": user.email})
        return None
    log_action(db, tabela="usuarios", acao="login", registro_id=user.id, usuario_id=user.id, origem="auth", valor_novo={"email": user.email, "perfil": user.perfil})
    return user
