from __future__ import annotations

import argparse
import importlib
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


MODULES = [
    "main",
    "dashboard.app",
    "operational_app.app",
    "src.api.main",
    "alembic",
    "src.crud.jornadas",
    "src.crud.ponto",
    "src.crud.banco_horas",
    "src.crud.documentos_obrigatorios",
    "src.crud.sst",
    "src.crud.workflows",
    "src.crud.tarefas",
    "src.crud.notificacoes",
    "src.services.alerts",
    "src.services.importacao_ponto",
    "src.services.workflow_service",
    "src.services.task_service",
    "src.services.notification_service",
    "src.services.calendar_service",
    "src.services.report_service",
    "scripts.seed_demo",
    "scripts.run_daily_checks",
    "scripts.migrate",
    "scripts.backup_postgres",
    "scripts.restore_postgres",
    "scripts.security_check",
]

SENSITIVE_GITIGNORE_PATTERNS = [
    "data/raw/",
    "data/processed/",
    "data/uploads/",
    "data/app/",
    "data/backups/",
    "data/logs/",
    ".env",
]


def check_imports() -> None:
    for module_name in MODULES:
        importlib.import_module(module_name)
        print(f"[ok] import {module_name}")


def run_pytest() -> None:
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(part for part in [str(ROOT), pythonpath] if part)
    result = subprocess.run([sys.executable, "-m", "pytest"], check=False, cwd=ROOT, env=env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def check_api_health() -> None:
    app_module = importlib.import_module("src.api.main")
    payload = app_module.health()
    assert payload["status"] in {"ok", "degraded"}
    print("[ok] api health")


def check_seed_blocked_in_production() -> None:
    seed_module = importlib.import_module("scripts.seed_demo")
    previous = os.environ.get("APP_ENV")
    os.environ["APP_ENV"] = "production"
    try:
        try:
            seed_module.ensure_not_production()
            raise AssertionError("Seed demo deveria falhar em producao.")
        except RuntimeError:
            print("[ok] seed bloqueado em producao")
    finally:
        if previous is None:
            os.environ.pop("APP_ENV", None)
        else:
            os.environ["APP_ENV"] = previous


def check_permissions() -> None:
    permissions = importlib.import_module("src.auth.permissions")
    assert permissions.has_permission("admin", "folha:update")
    assert not permissions.has_permission("visualizador", "folha:update")
    assert permissions.has_permission("dp", "ponto:approve")
    assert permissions.has_permission("dp", "workflows:create")
    assert permissions.has_permission("dp", "tarefas:update")
    assert permissions.has_permission("dp", "notificacoes:view")
    print("[ok] permissoes basicas")


def check_gitignore_patterns() -> None:
    content = (ROOT / ".gitignore").read_text(encoding="utf-8")
    missing = [pattern for pattern in SENSITIVE_GITIGNORE_PATTERNS if pattern not in content]
    if missing:
        raise AssertionError(f"Padroes sensiveis ausentes no .gitignore: {', '.join(missing)}")
    print("[ok] gitignore sensivel")


def check_not_versioned() -> None:
    for path_pattern in [".env", "data/raw", "data/uploads", "data/app"]:
        result = subprocess.run(
            ["git", "ls-files", path_pattern],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            raise AssertionError(f"Caminho versionado indevidamente: {path_pattern}")
    print("[ok] caminhos sensiveis fora do git")


def check_security() -> None:
    security_module = importlib.import_module("scripts.security_check")
    security_module.run_security_check(strict_production=False)
    print("[ok] security check")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args(argv)

    if args.fast and args.full:
        raise SystemExit("Use apenas um modo: --fast ou --full.")

    run_tests = not args.fast
    if args.full or (not args.fast and not args.full):
        run_tests = True

    if run_tests:
        run_pytest()
    check_imports()
    check_api_health()
    check_seed_blocked_in_production()
    check_permissions()
    check_gitignore_patterns()
    check_not_versioned()
    check_security()
    print("[ok] check_local concluido")


if __name__ == "__main__":
    main()
