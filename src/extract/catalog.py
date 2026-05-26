from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.extract.read_excel import inspect_workbook
from src.utils.text import detect_area_subarea, detect_sheet_type


def build_catalog(raw_dir: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_path = Path(raw_dir)
    catalog_rows = []
    error_rows = []
    for file_path in sorted(raw_path.glob("*.xlsx")):
        workbook_catalog, workbook_errors = inspect_workbook(file_path)
        for row in workbook_catalog:
            area, subarea = detect_area_subarea(row["arquivo"], row["aba"])
            row["area_detectada"] = area
            row["subarea_detectada"] = subarea
            row["tipo_aba"] = detect_sheet_type(row["aba"], row["arquivo"])
            catalog_rows.append(row)
        error_rows.extend(workbook_errors)
    return pd.DataFrame(catalog_rows), pd.DataFrame(error_rows)
