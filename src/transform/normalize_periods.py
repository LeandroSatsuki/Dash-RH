from __future__ import annotations

from calendar import monthrange
from datetime import datetime
from typing import Iterable

import pandas as pd


def build_period_dimension(periods: Iterable[dict]) -> pd.DataFrame:
    rows = []
    seen = set()
    for item in periods:
        ano = item.get("ano")
        mes_num = item.get("mes_num")
        mes_nome = item.get("mes_nome")
        competencia = item.get("competencia")
        if not ano or not mes_num or not competencia:
            continue
        key = (ano, mes_num)
        if key in seen:
            continue
        seen.add(key)
        start = datetime(ano, mes_num, 1)
        end = datetime(ano, mes_num, monthrange(ano, mes_num)[1])
        rows.append(
            {
                "periodo_id": competencia,
                "ano": ano,
                "mes_num": mes_num,
                "mes_nome": mes_nome,
                "competencia": competencia,
                "data_inicio_mes": start,
                "data_fim_mes": end,
            }
        )
    return pd.DataFrame(rows).sort_values(["ano", "mes_num"]).reset_index(drop=True)

