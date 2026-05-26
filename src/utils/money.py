from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from src.utils.numbers import to_number

MONEY_QUANT = Decimal("0.01")


def safe_decimal(value: Any) -> Decimal | None:
    if isinstance(value, Decimal):
        return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    numeric = to_number(value)
    if numeric is None:
        return None
    try:
        return Decimal(str(numeric)).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        return None


def parse_money_br(value: Any) -> Decimal | None:
    return safe_decimal(value)


def decimal_to_float_for_chart(value: Decimal | None) -> float | None:
    return None if value is None else float(value)


def format_brl(value: Any) -> str:
    decimal_value = safe_decimal(value)
    if decimal_value is None:
        return "R$ -"
    text = f"{decimal_value:,.2f}"
    return "R$ " + text.replace(",", "X").replace(".", ",").replace("X", ".")
