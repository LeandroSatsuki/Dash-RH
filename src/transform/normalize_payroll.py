from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.extract.read_excel import load_workbook_pair
from src.utils.text import detect_area_subarea, detect_sheet_type, is_error_value, parse_month_year, safe_divide, to_number


def _descriptor(ws, row: int, col: int) -> str:
    parts = []
    for offset in (-1, 0, 1):
        if row + offset < 1:
            continue
        value = ws.cell(row + offset, col).value
        if value not in (None, ""):
            parts.append(str(value))
    return " ".join(parts).strip().lower()


def _find_header_row(ws) -> int | None:
    for row in range(1, min(ws.max_row, 10) + 1):
        for col in range(1, min(ws.max_column, 10) + 1):
            value = ws.cell(row, col).value
            if value and "colaborador" in str(value).lower():
                return row
    return None


def _find_faturamento(ws_values) -> float | None:
    for row in range(1, min(ws_values.max_row, 8) + 1):
        for col in range(1, min(ws_values.max_column, 6) + 1):
            value = ws_values.cell(row, col).value
            if value and "faturamento" in str(value).lower():
                return to_number(ws_values.cell(row, col + 1).value)
    return None


def _map_columns(ws, header_row: int) -> dict[str, list[int]]:
    mapping = {
        "colaborador": [],
        "salario": [],
        "premios": [],
        "ajuda_custo": [],
        "alimentacao": [],
        "plano_saude": [],
        "beneficios": [],
        "encargos_inss": [],
        "fgts": [],
        "provisoes": [],
        "total_geral": [],
    }
    for col in range(1, ws.max_column + 1):
        descriptor = _descriptor(ws, header_row, col)
        if "colaborador" in descriptor:
            mapping["colaborador"].append(col)
        if "salario" in descriptor:
            mapping["salario"].append(col)
        if "premio" in descriptor:
            mapping["premios"].append(col)
        if "aj. custo" in descriptor or "aj custo" in descriptor:
            mapping["ajuda_custo"].append(col)
        if "aliment" in descriptor or "basica" in descriptor:
            mapping["alimentacao"].append(col)
            mapping["beneficios"].append(col)
        if "plano" in descriptor or "odont" in descriptor:
            mapping["plano_saude"].append(col)
            mapping["beneficios"].append(col)
        if "seguro" in descriptor:
            mapping["beneficios"].append(col)
        if descriptor.endswith("inss") or " inss" in descriptor:
            mapping["encargos_inss"].append(col)
        if descriptor.endswith("fgts") or " fgts" in descriptor:
            mapping["fgts"].append(col)
        if "ferias" in descriptor or "férias" in descriptor or "1/3" in descriptor or "13" in descriptor:
            mapping["provisoes"].append(col)
        if "total geral" in descriptor:
            mapping["total_geral"].append(col)
    return mapping


def _sum_columns(ws_values, row: int, columns: list[int]) -> float | None:
    values = [to_number(ws_values.cell(row, col).value) for col in columns]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return float(sum(values))


def _sheet_period(file_name: str, sheet_name: str) -> dict[str, Any]:
    explicit = parse_month_year(sheet_name)
    if explicit["competencia"]:
        return explicit
    file_period = parse_month_year(file_name)
    return file_period


def extract_payroll_facts(raw_dir: str | Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    raw_path = Path(raw_dir)
    for file_path in sorted(raw_path.glob("*.xlsx")):
        formula_wb, value_wb = load_workbook_pair(file_path)
        for sheet_name in formula_wb.sheetnames:
            if detect_sheet_type(sheet_name, file_path.name) != "fopag/folha":
                continue
            if "Analitic" in sheet_name or "Analitic" in file_path.name:
                continue
            ws_formula = formula_wb[sheet_name]
            ws_values = value_wb[sheet_name]
            header_row = _find_header_row(ws_formula)
            if not header_row:
                continue
            mapping = _map_columns(ws_formula, header_row)
            period = _sheet_period(file_path.name, sheet_name)
            area, subarea = detect_area_subarea(file_path.name, sheet_name)
            faturamento = _find_faturamento(ws_values)
            started = False
            for row in range(header_row + 1, ws_formula.max_row + 1):
                col_ref = mapping["colaborador"][0] if mapping["colaborador"] else 1
                collaborator = ws_values.cell(row, col_ref).value
                text = str(collaborator).strip().lower() if collaborator is not None else ""
                if collaborator not in (None, ""):
                    started = True
                if started and collaborator in (None, ""):
                    break
                if any(token in text for token in ["total", "desembolso", "faturamento"]):
                    break
                if not collaborator:
                    continue
                salario = _sum_columns(ws_values, row, mapping["salario"])
                premios = _sum_columns(ws_values, row, mapping["premios"])
                ajuda_custo = _sum_columns(ws_values, row, mapping["ajuda_custo"])
                alimentacao = _sum_columns(ws_values, row, mapping["alimentacao"])
                plano_saude = _sum_columns(ws_values, row, mapping["plano_saude"])
                beneficios = _sum_columns(ws_values, row, mapping["beneficios"])
                encargos_inss = _sum_columns(ws_values, row, mapping["encargos_inss"])
                fgts = _sum_columns(ws_values, row, mapping["fgts"])
                provisoes = _sum_columns(ws_values, row, mapping["provisoes"])
                total_geral = _sum_columns(ws_values, row, mapping["total_geral"])
                if total_geral is None:
                    total_geral = sum(
                        value
                        for value in [salario, premios, ajuda_custo, beneficios, encargos_inss, fgts, provisoes]
                        if value is not None
                    )
                rows.append(
                    {
                        "periodo_id": period["competencia"],
                        "area": area,
                        "subarea": subarea,
                        "colaborador": collaborator,
                        "salario": salario,
                        "premios": premios,
                        "ajuda_custo": ajuda_custo,
                        "alimentacao": alimentacao,
                        "plano_saude": plano_saude,
                        "beneficios": beneficios,
                        "encargos_inss": encargos_inss,
                        "fgts": fgts,
                        "provisoes": provisoes,
                        "total_geral": total_geral,
                        "percentual_custo": safe_divide(total_geral, faturamento),
                        "faturamento_referencia": faturamento,
                        "origem_arquivo": file_path.name,
                        "origem_aba": sheet_name,
                    }
                )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df[df["periodo_id"].notna()].reset_index(drop=True)

