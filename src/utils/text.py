from __future__ import annotations

import math
import re
import unicodedata
from datetime import timedelta
from typing import Any

import numpy as np

MONTH_ALIASES = {
    "jan": (1, "Janeiro"),
    "janeiro": (1, "Janeiro"),
    "fev": (2, "Fevereiro"),
    "fevereiro": (2, "Fevereiro"),
    "mar": (3, "Março"),
    "marco": (3, "Março"),
    "março": (3, "Março"),
    "abr": (4, "Abril"),
    "abril": (4, "Abril"),
    "mai": (5, "Maio"),
    "maio": (5, "Maio"),
    "jun": (6, "Junho"),
    "junho": (6, "Junho"),
    "jul": (7, "Julho"),
    "julho": (7, "Julho"),
    "ago": (8, "Agosto"),
    "agosto": (8, "Agosto"),
    "set": (9, "Setembro"),
    "setembro": (9, "Setembro"),
    "out": (10, "Outubro"),
    "outubro": (10, "Outubro"),
    "nov": (11, "Novembro"),
    "novembro": (11, "Novembro"),
    "dez": (12, "Dezembro"),
    "dezembro": (12, "Dezembro"),
}

CURRENT_YEAR_BY_FILENAME = {
    "indicadores folha adm": 2026,
    "indicadores folha comercial": 2026,
    "indicadores folha fabrica": 2026,
    "indicadores folha fábrica": 2026,
}

SUMMARY_SHEET_ALIASES = {
    "adm",
    "adm 2025",
    "geral",
    "comercial",
    "comercial 1",
    "com mg",
    "com rj",
    "comsp",
    "comercial 2025",
    "comercial 2023",
    "fabril",
    "fabril 2025",
}

PERCENT_KEYWORDS = {
    "taxa de absenteismo",
    "taxa de absenteísmo",
    "taxa de turnover",
    "encargos sobre a folha (%)",
    "encargos sobre folha %",
    "final",
    "inicial",
}


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def canonical_month(value: Any) -> tuple[int, str] | None:
    token = normalize_text(value)
    token = token.replace("-", " ").replace("/", " ")
    token = token.split(" ")[0] if token else token
    return MONTH_ALIASES.get(token)


def parse_year(text: Any) -> int | None:
    normalized = normalize_text(text)
    if not normalized:
        return None
    match = re.search(r"(20\d{2})", normalized)
    if match:
        return int(match.group(1))
    match = re.search(r"\b(\d{2})\b", normalized)
    if match:
        short = int(match.group(1))
        if 23 <= short <= 99:
            return 2000 + short
    return None


def parse_month_year(text: Any, default_year: int | None = None) -> dict[str, Any]:
    normalized = normalize_text(text)
    month_info = None
    year_hint = None
    for key, value in MONTH_ALIASES.items():
        if re.search(rf"\b{re.escape(key)}\b", normalized):
            month_info = value
            break
    if month_info is None:
        spaced = re.search(r"\b(0?[1-9]|1[0-2])\s+(20\d{2}|\d{2})\b", normalized)
        compact = re.search(r"\b(0[1-9]|1[0-2])([2-9]\d|20\d{2})\b", normalized)
        if spaced:
            month_num = int(spaced.group(1))
            month_info = next((info for info in MONTH_ALIASES.values() if info[0] == month_num), None)
            year_hint = int(spaced.group(2)) if len(spaced.group(2)) == 4 else 2000 + int(spaced.group(2))
        elif compact:
            month_num = int(compact.group(1))
            month_info = next((info for info in MONTH_ALIASES.values() if info[0] == month_num), None)
            year_hint = int(compact.group(2)) if len(compact.group(2)) == 4 else 2000 + int(compact.group(2))
    year = parse_year(normalized) or year_hint or default_year
    if month_info and year:
        month_num, month_name = month_info
        return {
            "ano": year,
            "mes_num": month_num,
            "mes_nome": month_name,
            "competencia": f"{year:04d}-{month_num:02d}",
        }
    return {"ano": year, "mes_num": None, "mes_nome": None, "competencia": None}


def current_year_from_filename(file_name: str) -> int | None:
    normalized = normalize_text(file_name)
    for key, year in CURRENT_YEAR_BY_FILENAME.items():
        if key in normalized:
            return year
    return parse_year(file_name)


def sheet_year(file_name: str, sheet_name: str) -> tuple[int | None, str]:
    explicit = parse_year(sheet_name)
    if explicit:
        return explicit, "explicito_na_aba"
    normalized_sheet = normalize_text(sheet_name)
    if normalized_sheet in {"adm", "geral", "comercial", "comercial 1", "com mg", "com rj", "comsp", "fabril"}:
        return current_year_from_filename(file_name), "inferido_pelo_arquivo"
    return current_year_from_filename(file_name), "inferido_pelo_arquivo"


def detect_area_subarea(file_name: str, sheet_name: str) -> tuple[str, str | None]:
    sheet = normalize_text(sheet_name)
    file_norm = normalize_text(file_name)
    if sheet == "geral":
        return "Geral", "Comercial Consolidado"
    if "adm" in sheet or "adm" in file_norm:
        return "ADM", None
    if "comercial" in file_norm:
        if sheet in {"comercial", "comercial 2025", "comercial 2023"}:
            return "Comercial", None
        if sheet == "comercial 1":
            return "Comercial", "Comercial 1"
        if sheet == "com mg":
            return "Comercial", "Com MG"
        if sheet == "com rj":
            return "Comercial", "Com RJ"
        if sheet == "comsp":
            return "Comercial", "ComSP"
        return "Comercial", None
    if sheet in {"comercial", "comercial 2025", "comercial 2023"}:
        return "Comercial", None
    if sheet == "comercial 1":
        return "Comercial", "Comercial 1"
    if sheet == "com mg":
        return "Comercial", "Com MG"
    if sheet == "com rj":
        return "Comercial", "Com RJ"
    if sheet == "comsp":
        return "Comercial", "ComSP"
    if "fabril" in sheet or "fabrica" in sheet or "fábrica" in sheet or "fabrica" in file_norm or "fabrica" in sheet:
        return "Fábrica", None
    return "Geral", None


def detect_sheet_type(sheet_name: str, file_name: str = "") -> str:
    sheet = normalize_text(sheet_name)
    if sheet in {
        "cadastro",
        "tb historico salarial",
        "tb afastamentos",
        "tb elegibilidade",
        "tb custo folha",
        "tb desligamentos",
        "lista suspensa",
    }:
        return "base cadastral"
    if sheet in SUMMARY_SHEET_ALIASES:
        return "resumo de indicadores"
    if "rotatividade" in sheet:
        return "rotatividade"
    if "calendario" in sheet:
        return "calendário"
    if "custo fopag" in sheet or sheet == "custo":
        return "custo fopag"
    if "fopag" in sheet or "folha" in sheet:
        return "fopag/folha"
    if "apur" in sheet:
        return "apuração"
    if "terceiros" in sheet:
        return "terceiros"
    if "prem" in sheet:
        return "premiação"
    if any(token in sheet for token in MONTH_ALIASES):
        return "mensal de colaboradores"
    return "outra"


def indicator_unit(indicator_name: str) -> str:
    normalized = normalize_text(indicator_name)
    if "(r$)" in normalized or "r$" in normalized:
        return "R$"
    if "(dias)" in normalized or "dias" in normalized:
        return "dias"
    if "(un)" in normalized:
        return "un"
    if "horas" in normalized or "hora extra" in normalized:
        return "horas"
    if normalized in PERCENT_KEYWORDS or "%" in normalized:
        return "%"
    return "valor"


def mask_document(value: Any) -> str | None:
    if value in (None, ""):
        return None
    digits = re.sub(r"\D", "", str(value))
    if len(digits) == 11:
        return f"***.***.***-{digits[-2:]}"
    if len(digits) == 14:
        return f"**.***.***/****-{digits[-2:]}"
    return "***"


def mask_name(value: Any) -> str | None:
    if value in (None, ""):
        return None
    parts = str(value).strip().split()
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0][0] + "***"
    return f"{parts[0][0]}*** {parts[-1][0]}***"


def is_error_value(value: Any) -> bool:
    return isinstance(value, str) and value.strip().startswith("#")


def error_type(value: Any) -> str | None:
    if is_error_value(value):
        return str(value).strip()
    return None


def to_number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, timedelta):
        return value.total_seconds() / 3600
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if math.isnan(value) or math.isinf(value):
            return None
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text or is_error_value(text):
            return None
        text = text.replace("R$", "").replace(".", "").replace(",", ".")
        try:
            return float(text)
        except ValueError:
            return None
    return None


def safe_divide(numerator: Any, denominator: Any) -> float | None:
    num = to_number(numerator)
    den = to_number(denominator)
    if num is None or den in (None, 0):
        return None
    return num / den


def confidence_label(has_error: bool, was_calculated: bool = False, inferred: bool = False) -> str:
    if has_error:
        return "Dado pendente / inconsistente"
    if was_calculated:
        return "calculado_pelo_pipeline"
    if inferred:
        return "inferido_com_contexto"
    return "extraido"


def flatten_list(values: list[list[Any]]) -> list[Any]:
    return [item for sublist in values for item in sublist]


def ensure_dataframe_numeric(series):
    return series.replace({np.nan: None})
