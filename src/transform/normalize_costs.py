from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.extract.read_excel import load_workbook_pair
from src.utils.excel_dates import competencia_from_date, convert_excel_date
from src.utils.text import canonical_month, detect_area_subarea, detect_sheet_type, parse_month_year, safe_divide, to_number


def _cost_context(ws_values) -> dict[str, dict[str, Any]]:
    context: dict[str, dict[str, Any]] = {}
    for row in range(3, min(ws_values.max_row, 15) + 1):
        period_value = convert_excel_date(ws_values.cell(row, 17).value)
        if not hasattr(period_value, "year") or period_value.year not in {2023, 2024, 2025, 2026}:
            continue
        competencia = competencia_from_date(period_value)
        if not competencia:
            continue
        context[competencia] = {
            "faturamento": to_number(ws_values.cell(row, 18).value),
            "custo_total": to_number(ws_values.cell(row, 19).value),
            "percentual_custo_faturamento": to_number(ws_values.cell(row, 20).value),
            "meta": to_number(ws_values.cell(row, 21).value),
            "colaboradores": to_number(ws_values.cell(row, 22).value),
            "faturamento_por_colaborador": to_number(ws_values.cell(row, 23).value),
        }
    return context


def _main_cost_block(ws_formula, ws_values, year: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    header_row = None
    for row in range(1, min(ws_formula.max_row, 5) + 1):
        months = [canonical_month(ws_formula.cell(row, col).value) for col in range(3, min(ws_formula.max_column, 16) + 1)]
        if sum(1 for item in months if item) >= 3:
            header_row = row
            break
    if header_row is None:
        return rows

    month_columns = []
    for col in range(3, min(ws_formula.max_column, 16) + 1):
        month_info = canonical_month(ws_formula.cell(header_row, col).value)
        if month_info:
            month_columns.append((col, month_info[0], month_info[1]))

    for row in range(header_row + 1, ws_formula.max_row + 1):
        category = ws_values.cell(row, 2).value
        if category in (None, "", "Total"):
            if str(category).strip().lower() == "total":
                break
            continue
        for col, month_num, month_name in month_columns:
            value = to_number(ws_values.cell(row, col).value)
            rows.append(
                {
                    "ano": year,
                    "mes_num": month_num,
                    "mes_nome": month_name,
                    "competencia": f"{year:04d}-{month_num:02d}" if year else None,
                    "categoria_custo": category,
                    "valor": value,
                    "origem_range": ws_formula.cell(row, col).coordinate,
                }
            )
    return rows


def extract_cost_facts(raw_dir: str | Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    raw_path = Path(raw_dir)
    for file_path in sorted(raw_path.glob("*.xlsx")):
        formula_wb, value_wb = load_workbook_pair(file_path)
        for sheet_name in formula_wb.sheetnames:
            if detect_sheet_type(sheet_name, file_path.name) != "custo fopag":
                continue
            ws_formula = formula_wb[sheet_name]
            ws_values = value_wb[sheet_name]
            area, subarea = detect_area_subarea(file_path.name, sheet_name)
            default_year = parse_month_year(sheet_name, default_year=parse_month_year(file_path.name).get("ano")).get("ano")
            context = _cost_context(ws_values)
            context_by_month = {}
            for competencia, ctx in context.items():
                month_num = int(str(competencia)[5:7])
                context_by_month[month_num] = {"competencia": competencia, **ctx}
            cost_rows = _main_cost_block(ws_formula, ws_values, default_year)
            for item in cost_rows:
                mapped = context_by_month.get(item["mes_num"])
                competencia = mapped["competencia"] if mapped else item["competencia"]
                ctx = context.get(competencia, {})
                rows.append(
                    {
                        "periodo_id": competencia,
                        "area": area,
                        "subarea": subarea,
                        "categoria_custo": item["categoria_custo"],
                        "valor": item["valor"],
                        "faturamento": ctx.get("faturamento"),
                        "custo_total": ctx.get("custo_total"),
                        "percentual_custo_faturamento": ctx.get("percentual_custo_faturamento")
                        if ctx.get("percentual_custo_faturamento") is not None
                        else safe_divide(ctx.get("custo_total"), ctx.get("faturamento")),
                        "meta": ctx.get("meta"),
                        "colaboradores": ctx.get("colaboradores"),
                        "faturamento_por_colaborador": ctx.get("faturamento_por_colaborador")
                        if ctx.get("faturamento_por_colaborador") is not None
                        else safe_divide(ctx.get("faturamento"), ctx.get("colaboradores")),
                        "origem_arquivo": file_path.name,
                        "origem_aba": sheet_name,
                    }
                )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df[df["periodo_id"].notna()].reset_index(drop=True)
