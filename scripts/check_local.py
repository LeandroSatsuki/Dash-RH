from __future__ import annotations

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
    "src.services.alerts",
    "src.services.importacao_ponto",
]


def check_imports() -> None:
    for module_name in MODULES:
        importlib.import_module(module_name)
        print(f"[ok] import {module_name}")


def run_pytest() -> None:
    result = subprocess.run([sys.executable, "-m", "pytest"], check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def check_api_health() -> None:
    app_module = importlib.import_module("src.api.main")
    assert app_module.health() == {"status": "ok"}
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
    assert permissions.has_permission("dp", "jornadas:create")
    assert permissions.has_permission("rh", "documentos_obrigatorios:view")
    print("[ok] permissoes basicas")


def main() -> None:
    run_pytest()
    check_imports()
    check_api_health()
    check_seed_blocked_in_production()
    check_permissions()
    print("[ok] check_local concluido")


if __name__ == "__main__":
    main()
