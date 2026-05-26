from __future__ import annotations

import math
import re
from datetime import timedelta
from typing import Any

import numpy as np
import pandas as pd

EXCEL_ERROR_VALUES = {
    "#DIV/0!",
    "#REF!",
    "#VALUE!",
    "#N/A",
    "#NAME?",
}

INVALID_TOKENS = {
    "",
    "-",
    "—",
    "–",
    "nan",
    "none",
    "null",
}


def _normalize_numeric_text(value: str) -> str:
    text = str(value).strip()
    text = text.replace("\u00a0", " ")
    text = text.replace("R$", "")
    text = text.replace("r$", "")
    text = text.replace(" ", "")
    return text


def to_number(value: Any) -> float | None:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, timedelta):
        return value.total_seconds() / 3600
    if isinstance(value, (int, float, np.number)) and not isinstance(value, bool):
        numeric = float(value)
        if math.isnan(numeric) or math.isinf(numeric):
            return None
        return numeric

    text = _normalize_numeric_text(str(value))
    if not text:
        return None

    upper_text = text.upper()
    if upper_text in EXCEL_ERROR_VALUES:
        return None
    if text.lower() in INVALID_TOKENS:
        return None

    is_percent = "%" in text
    text = text.replace("%", "")

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1]
    if text.startswith("+"):
        text = text[1:]
    elif text.startswith("-"):
        negative = True
        text = text[1:]

    text = re.sub(r"[^0-9,.-]", "", text)
    if not text or text in {".", ",", "-"}:
        return None

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(".", "").replace(",", ".")
    else:
        if text.count(".") > 1:
            parts = text.split(".")
            text = "".join(parts[:-1]) + "." + parts[-1]

    try:
        numeric = float(text)
    except ValueError:
        return None

    if negative:
        numeric *= -1
    if math.isnan(numeric) or math.isinf(numeric):
        return None
    if is_percent:
        numeric /= 100
    return numeric


def ensure_numeric_columns(df: pd.DataFrame, columns: list[str] | tuple[str, ...]) -> pd.DataFrame:
    converted = df.copy()
    for column in columns:
        if column not in converted.columns:
            converted[column] = np.nan
        converted[column] = pd.to_numeric(converted[column].map(to_number), errors="coerce")
    return converted
