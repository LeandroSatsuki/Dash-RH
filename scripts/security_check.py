from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.config import get_settings
from src.utils.logging_config import configure_logging, log_structured


logger = configure_logging("security_check")


def _is_tracked(path_pattern: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", path_pattern],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def run_security_check(*, strict_production: bool = False) -> None:
    settings = get_settings(validate=not strict_production, ensure_dirs=True)
    issues: list[str] = []

    if settings.app_env == "production" or strict_production:
        if len(settings.secret_key) < 16 or settings.secret_key.lower() == "change-me":
            issues.append("SECRET_KEY fraca para producao.")
        if settings.database_url.startswith("sqlite"):
            issues.append("SQLite bloqueado para producao. Use PostgreSQL.")
        if settings.admin_password == "Admin@123":
            issues.append("ADMIN_PASSWORD padrao insegura.")

    if settings.smtp_enabled and not settings.smtp_password:
        issues.append("SMTP_PASSWORD obrigatoria quando SMTP_ENABLED=true.")
    if settings.webhook_enabled and not settings.webhook_url:
        issues.append("WEBHOOK_URL obrigatoria quando WEBHOOK_ENABLED=true.")
    if not settings.upload_dir.exists():
        issues.append("UPLOAD_DIR nao existe.")
    if not settings.backup_dir.exists():
        issues.append("BACKUP_DIR nao existe.")

    for tracked in [".env", "data/raw", "data/uploads", "data/app"]:
        if _is_tracked(tracked):
            issues.append(f"Caminho sensivel versionado: {tracked}")

    if issues:
        log_structured(logger, 40, "security check falhou", issues=issues, app_env=settings.app_env)
        raise RuntimeError(" | ".join(issues))

    log_structured(logger, 20, "security check concluido", app_env=settings.app_env)


def main() -> None:
    run_security_check()


if __name__ == "__main__":
    main()
