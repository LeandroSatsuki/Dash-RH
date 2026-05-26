from __future__ import annotations

from datetime import date, datetime
from typing import Any

from openpyxl.utils.datetime import from_excel


def is_excel_serial(value: Any) -> bool:
    return isinstance(value, (int, float)) and 1 <= value <= 2958465


def convert_excel_date(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if is_excel_serial(value):
        try:
            return from_excel(value)
        except Exception:
            return value
    return value


def to_date_string_br(value: Any) -> str | None:
    dt = convert_excel_date(value)
    if isinstance(dt, datetime):
        return dt.strftime("%d/%m/%Y")
    return None


def competencia_from_date(value: Any) -> str | None:
    dt = convert_excel_date(value)
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m")
    return None

