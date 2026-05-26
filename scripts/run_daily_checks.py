from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.db.database import SessionLocal
from src.db.init_db import init_db
from src.services.scheduler_rules import run_daily_checks


def main() -> dict:
    init_db()
    with SessionLocal() as db:
        result = run_daily_checks(db)
    print(result)
    return result


if __name__ == "__main__":
    main()
