from __future__ import annotations

from sqlalchemy import select

from src.auth.security import hash_password
from src.db import models as _models  # noqa: F401
from src.db.database import Base, SessionLocal, engine
from src.db.models import Usuario
from src.services.audit_service import log_action
from src.utils.config import get_app_env, get_settings, is_development, is_production
from src.utils.logging_config import configure_logging, log_structured


logger = configure_logging("init_db")


def init_db() -> None:
    settings = get_settings(validate=True, ensure_dirs=True)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        admin_email = settings.admin_email
        admin_password = settings.admin_password

        if not is_development() and not admin_email:
            raise RuntimeError(f"APP_ENV={get_app_env()}: ADMIN_EMAIL e obrigatorio para criacao do admin inicial.")
        if not is_development() and not admin_password:
            raise RuntimeError(f"APP_ENV={get_app_env()}: ADMIN_PASSWORD e obrigatoria para criacao do admin inicial.")
        if is_production() and admin_password == "Admin@123":
            raise RuntimeError("APP_ENV=production: senha padrao insegura bloqueada para o usuario admin.")

        admin = db.scalar(select(Usuario).where(Usuario.email == admin_email))
        if admin is None:
            admin = Usuario(
                nome=settings.admin_name,
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
            log_structured(logger, 20, "usuario admin criado", app_env=get_app_env(), admin_email=admin_email)
        else:
            log_structured(logger, 20, "usuario admin ja existe", app_env=get_app_env(), admin_email=admin_email)


if __name__ == "__main__":
    init_db()
