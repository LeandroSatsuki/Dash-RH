from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


ALLOWED_APP_ENVS = {"development", "test", "staging", "homologation", "production"}
INSECURE_DEFAULTS = {"", "change-me", "changeme", "secret", "default", "admin@123"}


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    app_env: Literal["development", "test", "staging", "homologation", "production"]
    database_url: str
    secret_key: str
    upload_dir: Path
    backup_dir: Path
    admin_name: str
    admin_email: str
    admin_password: str
    smtp_enabled: bool
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_from: str
    webhook_enabled: bool
    webhook_url: str
    log_level: str
    log_to_file: bool


def _get_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default).lower()).strip().lower() in {"1", "true", "yes", "on"}


def _get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _validate_app_env(app_env: str) -> str:
    normalized = (app_env or "development").strip().lower()
    if normalized not in ALLOWED_APP_ENVS:
        raise ConfigError(f"APP_ENV invalido: {normalized}. Valores aceitos: {', '.join(sorted(ALLOWED_APP_ENVS))}.")
    return normalized


def _validate_path(name: str, value: str) -> Path:
    if not value:
        raise ConfigError(f"{name} e obrigatorio.")
    return Path(value)


def _validate_secret_key(settings: Settings) -> None:
    if settings.app_env != "production":
        return
    if settings.secret_key.strip().lower() in INSECURE_DEFAULTS or len(settings.secret_key.strip()) < 16:
        raise ConfigError("SECRET_KEY insegura para APP_ENV=production. Defina uma chave forte com pelo menos 16 caracteres.")


def _validate_database(settings: Settings) -> None:
    if settings.app_env != "production":
        return
    if not settings.database_url:
        raise ConfigError("DATABASE_URL e obrigatoria em producao.")
    if settings.database_url == "sqlite:///./data/app/dash_rh.db":
        raise ConfigError("DATABASE_URL padrao de desenvolvimento nao pode ser usada em producao.")


def _validate_admin(settings: Settings) -> None:
    if settings.app_env == "development":
        return
    if not settings.admin_email:
        raise ConfigError("ADMIN_EMAIL e obrigatorio fora de development.")
    if not settings.admin_password:
        raise ConfigError("ADMIN_PASSWORD e obrigatoria fora de development.")
    if settings.app_env == "production" and settings.admin_password == "Admin@123":
        raise ConfigError("ADMIN_PASSWORD com senha padrao insegura bloqueada para APP_ENV=production.")


def _validate_notification_channels(settings: Settings) -> None:
    if settings.smtp_enabled:
        missing = [name for name, value in {
            "SMTP_HOST": settings.smtp_host,
            "SMTP_PORT": str(settings.smtp_port or ""),
            "SMTP_USER": settings.smtp_user,
            "SMTP_PASSWORD": settings.smtp_password,
            "SMTP_FROM": settings.smtp_from,
        }.items() if not value]
        if missing:
            raise ConfigError(f"SMTP habilitado, mas faltam configuracoes: {', '.join(missing)}.")
    if settings.webhook_enabled and not settings.webhook_url:
        raise ConfigError("WEBHOOK_URL e obrigatoria quando WEBHOOK_ENABLED=true.")


def get_settings(*, validate: bool = True, ensure_dirs: bool = False) -> Settings:
    app_env = _validate_app_env(_get_env("APP_ENV", "development"))
    settings = Settings(
        app_env=app_env,  # type: ignore[arg-type]
        database_url=_get_env("DATABASE_URL", "sqlite:///./data/app/dash_rh.db"),
        secret_key=_get_env("SECRET_KEY", "change-me"),
        upload_dir=_validate_path("UPLOAD_DIR", _get_env("UPLOAD_DIR", "data/uploads")),
        backup_dir=_validate_path("BACKUP_DIR", _get_env("BACKUP_DIR", "data/backups")),
        admin_name=_get_env("ADMIN_NAME", "Administrador"),
        admin_email=_get_env("ADMIN_EMAIL", "admin@local.test" if app_env == "development" else ""),
        admin_password=_get_env("ADMIN_PASSWORD", "Admin@123" if app_env == "development" else ""),
        smtp_enabled=_get_bool("SMTP_ENABLED", False),
        smtp_host=_get_env("SMTP_HOST", ""),
        smtp_port=int(_get_env("SMTP_PORT", "0") or "0"),
        smtp_user=_get_env("SMTP_USER", ""),
        smtp_password=_get_env("SMTP_PASSWORD", ""),
        smtp_from=_get_env("SMTP_FROM", ""),
        webhook_enabled=_get_bool("WEBHOOK_ENABLED", False),
        webhook_url=_get_env("WEBHOOK_URL", ""),
        log_level=_get_env("LOG_LEVEL", "INFO").upper(),
        log_to_file=_get_bool("LOG_TO_FILE", False),
    )
    if validate:
        _validate_secret_key(settings)
        _validate_database(settings)
        _validate_admin(settings)
        _validate_notification_channels(settings)
    if ensure_dirs:
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        settings.backup_dir.mkdir(parents=True, exist_ok=True)
    return settings


def get_app_env() -> str:
    return get_settings(validate=False).app_env


def is_development() -> bool:
    return get_app_env() == "development"


def is_production() -> bool:
    return get_app_env() == "production"


def get_database_url() -> str:
    return get_settings(validate=False).database_url


def get_secret_key() -> str:
    return get_settings(validate=False).secret_key


def get_upload_dir() -> str:
    return str(get_settings(validate=False).upload_dir)


def get_backup_dir() -> str:
    return str(get_settings(validate=False).backup_dir)


def get_log_level() -> str:
    return get_settings(validate=False).log_level


def validate_runtime_settings() -> Settings:
    return get_settings(validate=True, ensure_dirs=True)
