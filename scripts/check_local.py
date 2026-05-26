from __future__ import annotations

import importlib
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
]


def check_imports() -> None:
    for module_name in MODULES:
        importlib.import_module(module_name)
        print(f"[ok] import {module_name}")


def run_pytest() -> None:
    result = subprocess.run([sys.executable, "-m", "pytest"], check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    run_pytest()
    check_imports()
    print("[ok] check_local concluido")


if __name__ == "__main__":
    main()
