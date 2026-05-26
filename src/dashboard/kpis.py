from __future__ import annotations

import pandas as pd


def latest_indicator_value(df: pd.DataFrame, indicator: str) -> tuple[float | None, str | None]:
    subset = df[df["indicador"].eq(indicator) & df["valor"].notna()].sort_values(["ano", "mes_num"])
    if subset.empty:
        return None, None
    row = subset.iloc[-1]
    return row["valor"], row["competencia"]


def metric_delta(df: pd.DataFrame, indicator: str) -> tuple[float | None, float | None]:
    subset = df[df["indicador"].eq(indicator) & df["valor"].notna()].sort_values(["ano", "mes_num"])
    if len(subset) < 2:
        return None, None
    current = subset.iloc[-1]["valor"]
    previous = subset.iloc[-2]["valor"]
    if current is None or previous is None:
        return None, None
    mom = current - previous
    yoy = None
    current_row = subset.iloc[-1]
    compare = subset[
        subset["competencia"].eq(f"{int(current_row['ano']) - 1:04d}-{int(current_row['mes_num']):02d}")
    ]
    if not compare.empty and compare.iloc[-1]["valor"] is not None:
        yoy = current - compare.iloc[-1]["valor"]
    return mom, yoy
