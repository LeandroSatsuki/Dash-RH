from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.extract.read_excel import load_workbook_pair
from src.utils.excel_dates import competencia_from_date, convert_excel_date
from src.utils.text import (
    canonical_month,
    confidence_label,
    detect_area_subarea,
    detect_sheet_type,
    indicator_unit,
    is_error_value,
    parse_month_year,
    sheet_year,
    to_number,
)


def _summary_sheet_rows(file_path: Path, sheet_name: str) -> list[dict[str, Any]]:
    formula_wb, value_wb = load_workbook_pair(file_path)
    ws_formula = formula_wb[sheet_name]
    ws_values = value_wb[sheet_name]
    year, year_source = sheet_year(file_path.name, sheet_name)
    area, subarea = detect_area_subarea(file_path.name, sheet_name)
    month_columns: list[tuple[int, int, str]] = []

    for col in range(3, ws_formula.max_column + 1):
        header = ws_formula.cell(1, col).value
        month_info = canonical_month(header)
        if month_info:
            month_num, month_name = month_info
            month_columns.append((col, month_num, month_name))

    rows = []
    for row in range(2, ws_formula.max_row + 1):
        indicator = ws_formula.cell(row, 1).value
        if indicator in (None, ""):
            continue
        for col, month_num, month_name in month_columns:
            formula_cell = ws_formula.cell(row, col)
            value_cell = ws_values.cell(row, col)
            value = value_cell.value
            formula = formula_cell.value if isinstance(formula_cell.value, str) and formula_cell.value.startswith("=") else None
            has_error = is_error_value(value) or is_error_value(formula)
            numeric_value = to_number(value)
            rows.append(
                {
                    "ano": year,
                    "mes": month_name,
                    "mes_num": month_num,
                    "competencia": f"{year:04d}-{month_num:02d}" if year else None,
                    "area": area,
                    "subarea": subarea,
                    "indicador": indicator,
                    "valor": numeric_value,
                    "unidade": indicator_unit(str(indicator)),
                    "origem_arquivo": file_path.name,
                    "origem_aba": sheet_name,
                    "origem_range": formula_cell.coordinate,
                    "confiabilidade": confidence_label(has_error, inferred=year_source != "explicito_na_aba"),
                    "formula_origem": formula,
                }
            )
    return rows


def _rotatividade_rows(file_path: Path, sheet_name: str) -> list[dict[str, Any]]:
    formula_wb, value_wb = load_workbook_pair(file_path)
    ws_formula = formula_wb[sheet_name]
    ws_values = value_wb[sheet_name]
    area, subarea = detect_area_subarea(file_path.name, sheet_name)
    turnover_year = to_number(ws_values["D2"].value)
    abs_year = to_number(ws_values["L2"].value)
    rows = []

    left_map = {
        2: "Admissões",
        3: "Desligamentos",
        4: "Colaboradores",
        5: "Turnover",
        6: "Média Turnover",
        7: "Meta Turnover",
    }
    right_map = {
        10: "Horas Programadas",
        11: "Horas não Produtivas",
        12: "Taxa de Absenteísmo",
        13: "Média Absenteísmo",
        14: "Meta Absenteísmo",
    }

    for row in range(4, 16):
        month_value = ws_values.cell(row, 1).value
        month_info = canonical_month(month_value)
        if not month_info:
            continue
        month_num, month_name = month_info
        for col, indicator in left_map.items():
            cell_formula = ws_formula.cell(row, col)
            cell_value = ws_values.cell(row, col).value
            rows.append(
                {
                    "ano": int(turnover_year) if turnover_year else None,
                    "mes": month_name,
                    "mes_num": month_num,
                    "competencia": f"{int(turnover_year):04d}-{month_num:02d}" if turnover_year else None,
                    "area": area,
                    "subarea": subarea,
                    "indicador": indicator,
                    "valor": to_number(cell_value),
                    "unidade": "%" if "turnover" in indicator.lower() or "meta" in indicator.lower() else "valor",
                    "origem_arquivo": file_path.name,
                    "origem_aba": sheet_name,
                    "origem_range": cell_formula.coordinate,
                    "confiabilidade": confidence_label(is_error_value(cell_value)),
                    "formula_origem": cell_formula.value if isinstance(cell_formula.value, str) and cell_formula.value.startswith("=") else None,
                }
            )
        for col, indicator in right_map.items():
            cell_formula = ws_formula.cell(row, col)
            cell_value = ws_values.cell(row, col).value
            rows.append(
                {
                    "ano": int(abs_year) if abs_year else None,
                    "mes": month_name,
                    "mes_num": month_num,
                    "competencia": f"{int(abs_year):04d}-{month_num:02d}" if abs_year else None,
                    "area": area,
                    "subarea": subarea,
                    "indicador": indicator,
                    "valor": to_number(cell_value),
                    "unidade": "%" if "absente" in indicator.lower() or "meta" in indicator.lower() else "horas",
                    "origem_arquivo": file_path.name,
                    "origem_aba": sheet_name,
                    "origem_range": cell_formula.coordinate,
                    "confiabilidade": confidence_label(is_error_value(cell_value)),
                    "formula_origem": cell_formula.value if isinstance(cell_formula.value, str) and cell_formula.value.startswith("=") else None,
                }
            )
    return rows


def _commercial_special_rows(file_path: Path) -> list[dict[str, Any]]:
    formula_wb, value_wb = load_workbook_pair(file_path)
    rows = []
    for sheet_name in value_wb.sheetnames:
        if "Premiação - CLT" in sheet_name:
            ws = value_wb[sheet_name]
            period = parse_month_year(sheet_name)
            total = 0.0
            for row in range(2, ws.max_row + 1):
                value = to_number(ws.cell(row, 9).value)
                if value is not None:
                    total += value
            rows.append(
                {
                    "ano": period["ano"],
                    "mes": period["mes_nome"],
                    "mes_num": period["mes_num"],
                    "competencia": period["competencia"],
                    "area": "Comercial",
                    "subarea": None,
                    "indicador": "Premiação CLT",
                    "valor": total if total else None,
                    "unidade": "R$",
                    "origem_arquivo": file_path.name,
                    "origem_aba": sheet_name,
                    "origem_range": "I2:I9999",
                    "confiabilidade": confidence_label(False),
                    "formula_origem": None,
                }
            )
        if "Premiação - MEI" in sheet_name:
            ws = value_wb[sheet_name]
            period = parse_month_year(sheet_name)
            total = 0.0
            count = 0
            for row in range(2, ws.max_row + 1):
                value = to_number(ws.cell(row, 8).value)
                if value is not None:
                    total += value
                    count += 1
            rows.append(
                {
                    "ano": period["ano"],
                    "mes": period["mes_nome"],
                    "mes_num": period["mes_num"],
                    "competencia": period["competencia"],
                    "area": "Comercial",
                    "subarea": None,
                    "indicador": "Premiação MEI",
                    "valor": total if count else None,
                    "unidade": "R$",
                    "origem_arquivo": file_path.name,
                    "origem_aba": sheet_name,
                    "origem_range": "H2:H9999",
                    "confiabilidade": confidence_label(count == 0),
                    "formula_origem": None,
                }
            )
    return rows


def extract_indicator_facts(raw_dir: str | Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    raw_path = Path(raw_dir)
    for file_path in sorted(raw_path.glob("*.xlsx")):
        formula_wb, _ = load_workbook_pair(file_path)
        for sheet_name in formula_wb.sheetnames:
            sheet_type = detect_sheet_type(sheet_name, file_path.name)
            if sheet_type == "resumo de indicadores":
                rows.extend(_summary_sheet_rows(file_path, sheet_name))
            elif sheet_type == "rotatividade":
                rows.extend(_rotatividade_rows(file_path, sheet_name))
        if "comercial" in file_path.name.lower():
            rows.extend(_commercial_special_rows(file_path))

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df[df["competencia"].notna()].copy()
    df["periodo_id"] = df["competencia"]
    return df.sort_values(["area", "subarea", "ano", "mes_num", "indicador"]).reset_index(drop=True)

