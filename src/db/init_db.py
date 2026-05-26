from __future__ import annotations

import os

from sqlalchemy import select

from src.auth.security import hash_password
from src.db import models as _models  # noqa: F401
from src.db.database import Base, SessionLocal, engine
from src.db.models import Usuario
from src.services.audit_service import log_action
from src.utils.config import get_app_env, is_development, is_production


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@local.test" if is_development() else "").strip()
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin@123" if is_development() else "")

        if not is_development() and not admin_email:
            raise RuntimeError(f"APP_ENV={get_app_env()}: ADMIN_EMAIL e obrigatorio para criacao do admin inicial.")
        if not is_development() and not admin_password:
            raise RuntimeError(f"APP_ENV={get_app_env()}: ADMIN_PASSWORD e obrigatoria para criacao do admin inicial.")
        if is_production() and admin_password == "Admin@123":
            raise RuntimeError("APP_ENV=production: senha padrao insegura bloqueada para o usuario admin.")

        admin = db.scalar(select(Usuario).where(Usuario.email == admin_email))
        if admin is None:
            admin = Usuario(
                nome=os.getenv("ADMIN_NAME", "Administrador"),
                email=admin_email,
                senha_hash=hash_password(admin_password),
                perfil="admin",
                ativo=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            log_action(
                db,
                tabela="usuarios",
                acao="bootstrap_admin",
                registro_id=admin.id,
                usuario_id=admin.id,
                origem="init_db",
                valor_novo={"email": admin.email, "perfil": admin.perfil},
            )
            print(f"Usuario admin criado com seguranca para APP_ENV={get_app_env()}: {admin_email}")
        else:
            print(f"Usuario admin ja existe para APP_ENV={get_app_env()}: {admin_email}")


if __name__ == "__main__":
    init_db()
