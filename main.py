from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.dashboard.kpis import latest_indicator_value, metric_delta
from src.extract.catalog import build_catalog
from src.transform.normalize_costs import extract_cost_facts
from src.transform.normalize_indicators import extract_indicator_facts
from src.transform.normalize_payroll import extract_payroll_facts
from src.transform.normalize_people import extract_people_dimensions
from src.transform.normalize_periods import build_period_dimension
from src.utils.text import confidence_label, safe_divide
from src.validate.quality import build_data_quality, write_quality_reports


PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"


def ensure_directories() -> None:
    for path in [RAW_DIR, PROCESSED_DIR, REPORTS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def stage_raw_files() -> None:
    for file_path in PROJECT_ROOT.glob("*.xlsx"):
        target = RAW_DIR / file_path.name
        if not target.exists():
            shutil.copy2(file_path, target)


def save_dataset(df: pd.DataFrame, name: str) -> None:
    csv_path = PROCESSED_DIR / f"{name}.csv"
    parquet_path = PROCESSED_DIR / f"{name}.parquet"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    parquet_df = df.copy()
    for column in parquet_df.select_dtypes(include=["object", "string"]).columns:
        parquet_df[column] = parquet_df[column].map(lambda value: None if pd.isna(value) else str(value))
    parquet_df.to_parquet(parquet_path, index=False)


def first_valid(series: pd.Series):
    for value in series:
        if pd.notna(value):
            return value
    return None


def build_dim_area(*frames: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for df in frames:
        if df is None or df.empty:
            continue
        required = {"area", "origem_arquivo", "origem_aba"}
        if not required.issubset(df.columns):
            continue
        subset = df[["area", "subarea", "origem_arquivo", "origem_aba"]].drop_duplicates()
        rows.append(subset)
    if not rows:
        return pd.DataFrame(columns=["area_id", "area", "subarea", "origem_arquivo", "origem_aba"])
    combined = pd.concat(rows, ignore_index=True).drop_duplicates().reset_index(drop=True)
    combined.insert(0, "area_id", combined.index + 1)
    return combined


def build_movimentacao(indicators: pd.DataFrame) -> pd.DataFrame:
    if indicators.empty:
        return pd.DataFrame()
    relevant = indicators[
        indicators["indicador"].isin(
            [
                "Efetivo Inicial (Un)",
                "Efetivo Final (Un)",
                "Efetivo Médio",
                "Novas Contratações (Un)",
                "Admissões",
                "Desligamentos (Un)",
                "Desligamentos",
                "Taxa de Turnover",
                "Turnover",
                "Colaboradores",
                "Meta Turnover",
            ]
        )
    ].copy()
    if relevant.empty:
        return pd.DataFrame()
    grouped = (
        relevant.sort_values(["competencia", "indicador"])
        .groupby(["periodo_id", "area", "subarea", "indicador"], dropna=False)
        .agg(
            valor=("valor", first_valid),
            origem_arquivo=("origem_arquivo", lambda x: "; ".join(sorted(set(x)))),
            origem_aba=("origem_aba", lambda x: "; ".join(sorted(set(x)))),
        )
        .reset_index()
    )
    pivot = grouped.pivot_table(
        index=["periodo_id", "area", "subarea"], columns="indicador", values="valor", aggfunc="first"
    ).reset_index()
    origin = grouped.groupby(["periodo_id", "area", "subarea"], dropna=False).agg(
        origem_arquivo=("origem_arquivo", lambda x: "; ".join(sorted(set(x)))),
        origem_aba=("origem_aba", lambda x: "; ".join(sorted(set(x)))),
    )
    pivot = pivot.merge(origin.reset_index(), on=["periodo_id", "area", "subarea"], how="left")
    def _col(name: str) -> pd.Series:
        return pivot[name] if name in pivot.columns else pd.Series([None] * len(pivot), index=pivot.index)

    pivot["admissoes"] = _col("Novas Contratações (Un)").combine_first(_col("Admissões"))
    pivot["desligamentos"] = _col("Desligamentos (Un)").combine_first(_col("Desligamentos"))
    pivot["efetivo_inicial"] = _col("Efetivo Inicial (Un)").combine_first(_col("Colaboradores"))
    pivot["efetivo_final"] = _col("Efetivo Final (Un)")
    pivot["efetivo_medio"] = _col("Efetivo Médio")
    pivot["turnover"] = _col("Taxa de Turnover").combine_first(_col("Turnover"))
    calculated = pivot["turnover"].isna()
    recalculated = pivot[calculated].apply(
        lambda row: safe_divide(
            ((row.get("desligamentos") or 0) + (row.get("admissoes") or 0)) / 2,
            row.get("Colaboradores"),
        ),
        axis=1,
    )
    pivot.loc[calculated, "turnover"] = recalculated.apply(lambda x: np.nan if x is None else float(x))
    return pivot[
        [
            "periodo_id",
            "area",
            "subarea",
            "admissoes",
            "desligamentos",
            "efetivo_inicial",
            "efetivo_final",
            "efetivo_medio",
            "turnover",
            "origem_arquivo",
            "origem_aba",
        ]
    ].sort_values(["periodo_id", "area", "subarea"])


def build_absenteismo(indicators: pd.DataFrame) -> pd.DataFrame:
    if indicators.empty:
        return pd.DataFrame()
    relevant = indicators[
        indicators["indicador"].isin(
            [
                "Afastamentos + Faltas (dias)",
                "Afastamentos (dias)",
                "Férias (dias não produtivos)",
                "Dias Úteis",
                "Dias Programados",
                "Dias Produtivos",
                "Dias não Produtivos",
                "Horas Programadas",
                "Horas não Produtivas",
                "Taxa de Absenteísmo",
                "Meta Absenteísmo",
            ]
        )
    ].copy()
    if relevant.empty:
        return pd.DataFrame()
    grouped = (
        relevant.groupby(["periodo_id", "area", "subarea", "indicador"], dropna=False)
        .agg(
            valor=("valor", first_valid),
            origem_arquivo=("origem_arquivo", lambda x: "; ".join(sorted(set(x)))),
            origem_aba=("origem_aba", lambda x: "; ".join(sorted(set(x)))),
        )
        .reset_index()
    )
    pivot = grouped.pivot_table(
        index=["periodo_id", "area", "subarea"], columns="indicador", values="valor", aggfunc="first"
    ).reset_index()
    origin = grouped.groupby(["periodo_id", "area", "subarea"], dropna=False).agg(
        origem_arquivo=("origem_arquivo", lambda x: "; ".join(sorted(set(x)))),
        origem_aba=("origem_aba", lambda x: "; ".join(sorted(set(x)))),
    )
    pivot = pivot.merge(origin.reset_index(), on=["periodo_id", "area", "subarea"], how="left")
    def _col(name: str) -> pd.Series:
        return pivot[name] if name in pivot.columns else pd.Series([None] * len(pivot), index=pivot.index)

    pivot["afastamentos_dias"] = _col("Afastamentos + Faltas (dias)").combine_first(_col("Afastamentos (dias)"))
    pivot["faltas_dias"] = None
    pivot["ferias_dias"] = _col("Férias (dias não produtivos)")
    pivot["dias_uteis"] = _col("Dias Úteis")
    pivot["dias_programados"] = _col("Dias Programados")
    pivot["dias_produtivos"] = _col("Dias Produtivos")
    pivot["dias_nao_produtivos"] = _col("Dias não Produtivos")
    pivot["horas_programadas"] = _col("Horas Programadas")
    pivot["horas_nao_produtivas"] = _col("Horas não Produtivas")
    pivot["taxa_absenteismo"] = _col("Taxa de Absenteísmo")
    calc_mask = pivot["taxa_absenteismo"].isna()
    recalculated = pivot[calc_mask].apply(
        lambda row: safe_divide(row.get("horas_nao_produtivas"), row.get("horas_programadas"))
        if row.get("horas_programadas") not in (None, 0)
        else safe_divide(row.get("dias_nao_produtivos"), row.get("dias_programados")),
        axis=1,
    )
    pivot.loc[calc_mask, "taxa_absenteismo"] = recalculated.apply(lambda x: np.nan if x is None else float(x))
    return pivot[
        [
            "periodo_id",
            "area",
            "subarea",
            "afastamentos_dias",
            "faltas_dias",
            "ferias_dias",
            "dias_uteis",
            "dias_programados",
            "dias_produtivos",
            "dias_nao_produtivos",
            "horas_programadas",
            "horas_nao_produtivas",
            "taxa_absenteismo",
            "origem_arquivo",
            "origem_aba",
        ]
    ].sort_values(["periodo_id", "area", "subarea"])


def append_calculated_indicators(indicators: pd.DataFrame, movimentacao: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in movimentacao.iterrows():
        if pd.notna(row.get("efetivo_inicial")) and pd.notna(row.get("efetivo_final")):
            rows.append(
                {
                    "periodo_id": row["periodo_id"],
                    "ano": int(str(row["periodo_id"])[:4]),
                    "mes_num": int(str(row["periodo_id"])[5:7]),
                    "mes": None,
                    "area": row["area"],
                    "subarea": row["subarea"],
                    "indicador": "Saldo de Headcount",
                    "valor": (row.get("admissoes") or 0) - (row.get("desligamentos") or 0),
                    "unidade": "un",
                    "origem_arquivo": row["origem_arquivo"],
                    "origem_aba": row["origem_aba"],
                    "origem_range": "calculado_pelo_pipeline",
                    "confiabilidade": confidence_label(False, was_calculated=True),
                    "formula_origem": "Novas Contratações - Desligamentos",
                    "competencia": row["periodo_id"],
                }
            )
            rows.append(
                {
                    "periodo_id": row["periodo_id"],
                    "ano": int(str(row["periodo_id"])[:4]),
                    "mes_num": int(str(row["periodo_id"])[5:7]),
                    "mes": None,
                    "area": row["area"],
                    "subarea": row["subarea"],
                    "indicador": "Variação Headcount %",
                    "valor": safe_divide((row.get("efetivo_final") or 0) - (row.get("efetivo_inicial") or 0), row.get("efetivo_inicial")),
                    "unidade": "%",
                    "origem_arquivo": row["origem_arquivo"],
                    "origem_aba": row["origem_aba"],
                    "origem_range": "calculado_pelo_pipeline",
                    "confiabilidade": confidence_label(False, was_calculated=True),
                    "formula_origem": "(Efetivo Final - Efetivo Inicial) / Efetivo Inicial",
                    "competencia": row["periodo_id"],
                }
            )
            if pd.notna(row.get("efetivo_medio")):
                rows.append(
                    {
                        "periodo_id": row["periodo_id"],
                        "ano": int(str(row["periodo_id"])[:4]),
                        "mes_num": int(str(row["periodo_id"])[5:7]),
                        "mes": None,
                        "area": row["area"],
                        "subarea": row["subarea"],
                        "indicador": "Turnover Ajustado",
                        "valor": safe_divide(
                            ((row.get("desligamentos") or 0) + (row.get("admissoes") or 0)) / 2,
                            row.get("efetivo_medio"),
                        ),
                        "unidade": "%",
                        "origem_arquivo": row["origem_arquivo"],
                        "origem_aba": row["origem_aba"],
                        "origem_range": "calculado_pelo_pipeline",
                        "confiabilidade": confidence_label(False, was_calculated=True),
                        "formula_origem": "((Desligamentos + Admissões) / 2) / Efetivo Médio",
                        "competencia": row["periodo_id"],
                    }
                )
    if not rows:
        return indicators
    extra = pd.DataFrame(rows)
    extra["mes"] = extra["mes"].fillna(extra["mes_num"].map({
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }))
    return pd.concat([indicators, extra], ignore_index=True, sort=False)


def build_metric_dictionary() -> str:
    items = {
        "Efetivo Inicial": ("Headcount no início do período.", "Valor extraído das abas resumo ou rotatividade.", "Resumo/rotatividade.", "Pode divergir quando há erro de fórmula.", "extraída"),
        "Efetivo Final": ("Headcount no fim do período.", "Valor extraído das abas resumo.", "Resumo de indicadores.", "Depende da consistência de admissões e desligamentos.", "extraída"),
        "Efetivo Médio": ("Média entre efetivo inicial e final.", "(Efetivo Inicial + Efetivo Final) / 2", "Resumo ou calculado pelo pipeline.", "Quando recalculado, usa apenas headcount disponível.", "extraída/calculada"),
        "Admissões": ("Entradas no mês.", "Novas Contratações (Un) ou Admissões.", "Resumo/rotatividade.", "Pode não refletir subáreas sem aba própria.", "extraída"),
        "Desligamentos": ("Saídas no mês.", "Desligamentos (Un) ou Desligamentos.", "Resumo/rotatividade.", "Erros em rotatividade afetam a taxa.", "extraída"),
        "Turnover": ("Rotatividade principal.", "((Desligamentos + Admissões) / 2) / Total de Colaboradores", "Resumo/rotatividade.", "Se Total de Colaboradores estiver ausente, manter inconsistente.", "extraída/calculada"),
        "Turnover Ajustado": ("Rotatividade com efetivo médio.", "((Desligamentos + Admissões) / 2) / Efetivo Médio", "calculado_pelo_pipeline.", "Só existe quando há efetivo médio.", "calculada"),
        "Afastamentos": ("Ausências por afastamento.", "Valor da planilha.", "Resumo/afastamentos.", "Em algumas abas vem somado com faltas.", "extraída"),
        "Faltas": ("Faltas no período.", "Valor da planilha.", "Resumo.", "Nem sempre separado dos afastamentos.", "extraída"),
        "Férias": ("Dias não produtivos por férias.", "Valor da planilha.", "Resumo.", "Pode estar zerado em meses sem férias lançadas.", "extraída"),
        "Dias Programados": ("Dias previstos para trabalho.", "Valor da planilha.", "Resumo.", "Pode ser calculado via efetivo médio em algumas abas.", "extraída"),
        "Dias Produtivos": ("Dias efetivamente produtivos.", "Dias Programados - Dias não Produtivos", "Resumo/calculado.", "Mantido como extraído quando confiável.", "extraída/calculada"),
        "Dias não Produtivos": ("Dias perdidos.", "Afastamentos + Faltas + Férias quando explícito.", "Resumo.", "Não supõe faltas se a planilha não separar.", "extraída"),
        "Horas Programadas": ("Horas previstas.", "Valor da planilha.", "Resumo/rotatividade.", "Não arredondado internamente.", "extraída"),
        "Horas não Produtivas": ("Horas perdidas.", "Valor da planilha ou cálculo proporcional explícito.", "Resumo/rotatividade.", "Sem regra explícita, não converte dias em horas.", "extraída"),
        "Taxa de Absenteísmo": ("Percentual de horas ou dias perdidos.", "Horas não Produtivas / Horas Programadas; fallback Dias não Produtivos / Dias Programados", "Resumo/rotatividade/calculado.", "Só usa fallback se não houver horas.", "extraída/calculada"),
        "Folha Líquida": ("Valor líquido da folha.", "Valor da planilha.", "Resumo/Fopag Analitic.", "Pode haver dependência de fórmulas legadas.", "extraída"),
        "Folha Bruta": ("Valor bruto da folha.", "Valor da planilha.", "Resumo/Fopag.", "Pode depender de consolidações legadas.", "extraída"),
        "Salário Per Capita": ("Folha por efetivo.", "Folha Bruta / Efetivo considerado", "Resumo/calculado.", "Sem efetivo confiável, manter inconsistente.", "extraída/calculada"),
        "Comissão": ("Comissões comerciais.", "Valor da planilha.", "Resumo Comercial/Custo.", "Pode estar ausente em meses sem apuração.", "extraída"),
        "DSR": ("Descanso semanal remunerado associado.", "Valor da planilha.", "Resumo Comercial.", "Pode estar zerado.", "extraída"),
        "Hora Extra": ("Horas extras.", "Valor da planilha.", "Resumo Comercial/Fabril.", "Timedelta convertido para horas.", "extraída"),
        "Hora Extra + DSR": ("Custo financeiro de HE + DSR.", "Valor da planilha.", "Resumo Comercial/Fabril.", "Pode estar zerado em meses sem evento.", "extraída"),
        "Valor de Tributos": ("Soma dos tributos da folha.", "Valor da planilha.", "Resumo.", "Erros #REF! precisam correção manual.", "extraída"),
        "INSS Patronal": ("Encargo patronal de INSS.", "Valor da planilha.", "Resumo/Fopag/Custo.", "Pode não existir separado em todas as áreas.", "extraída"),
        "FGTS": ("Encargo FGTS.", "Valor da planilha.", "Resumo/Fopag/Custo.", "Erros de fórmula afetam a visão mensal.", "extraída"),
        "Encargos sobre Folha %": ("Percentual de encargos.", "Valor de Tributos / Folha Bruta", "Resumo/calculado.", "Mantido inconsistente em divisão por zero.", "extraída/calculada"),
        "Custo Total": ("Soma do custo da folha e correlatos.", "Linha total ou soma das categorias quando confiável.", "Custo Fopag/Custo.", "Quando total não é confiável, usa soma das categorias.", "extraída/calculada"),
        "Custo / Faturamento %": ("Participação do custo no faturamento.", "Custo Total / Faturamento", "Custo Fopag.", "Sem faturamento, manter pendente.", "extraída/calculada"),
        "Faturamento por Colaborador": ("Produtividade financeira por pessoa.", "Faturamento / Colaboradores", "Custo Fopag.", "Sem colaboradores ou faturamento, manter pendente.", "extraída/calculada"),
        "Benefícios": ("Custo agregado de benefícios.", "Soma das colunas de benefício.", "TB_Elegibilidade/Fopag.", "Pode variar conforme layout da aba.", "extraída/calculada"),
        "Provisões": ("Provisões de férias/13º e similares.", "Valor da planilha.", "Custo Fopag/Fopag.", "Agrupa apenas o que estiver explícito.", "extraída"),
        "Premiação": ("Premiações e incentivos.", "Valor da planilha.", "Custo Fopag/Premiação CLT/MEI.", "MEI só entra quando há valores na aba.", "extraída"),
        "Terceiros": ("Custos com terceiros.", "Categorias MEI/Freelancer/Terceiros.", "Custo Fopag/Terceiros.", "Nem todas as abas trazem período explícito.", "extraída"),
    }
    lines = ["# Dicionário de Métricas", ""]
    for nome, (descricao, formula, fonte, limitacoes, origem) in items.items():
        lines.extend(
            [
                f"## {nome}",
                f"- Descrição: {descricao}",
                f"- Fórmula: {formula}",
                f"- Fonte: {fonte}",
                f"- Limitações: {limitacoes}",
                f"- Extraída ou calculada: {origem}",
                "",
            ]
        )
    return "\n".join(lines)


def build_executive_reports(
    indicators: pd.DataFrame,
    cost_df: pd.DataFrame,
    quality: dict[str, Any],
) -> None:
    latest_rows = []
    for indicator in [
        "Efetivo Final (Un)",
        "Efetivo Médio",
        "Admissões",
        "Desligamentos",
        "Turnover",
        "Taxa de Absenteísmo",
        "Folha Bruta (R$)",
        "Custo Total",
        "Custo / Faturamento %",
        "Faturamento por Colaborador",
    ]:
        value, competencia = latest_indicator_value(indicators, indicator)
        mom, yoy = metric_delta(indicators, indicator)
        latest_rows.append(
            {
                "Indicador": indicator,
                "Competência": competencia,
                "Valor": value,
                "Variação MoM": mom,
                "Variação YoY": yoy,
            }
        )
    kpi_df = pd.DataFrame(latest_rows)

    observations = []
    turnover = indicators[indicators["indicador"].eq("Turnover")][["competencia", "valor", "area", "subarea"]]
    meta_turnover = indicators[indicators["indicador"].eq("Meta Turnover")][["competencia", "valor", "area", "subarea"]]
    if not turnover.empty and not meta_turnover.empty:
        compare = turnover.merge(meta_turnover, on=["competencia", "area", "subarea"], suffixes=("_turnover", "_meta"))
        compare = compare[compare["valor_turnover"] > compare["valor_meta"]]
        for _, row in compare.head(10).iterrows():
            observations.append(
                f"Em {row['competencia']}, a taxa de turnover está acima da meta informada na aba de rotatividade para {row['area']}."
            )

    abs_df = indicators[indicators["indicador"].eq("Taxa de Absenteísmo")][["competencia", "valor", "area", "subarea"]]
    meta_abs = indicators[indicators["indicador"].eq("Meta Absenteísmo")][["competencia", "valor", "area", "subarea"]]
    if not abs_df.empty and not meta_abs.empty:
        compare = abs_df.merge(meta_abs, on=["competencia", "area", "subarea"], suffixes=("_abs", "_meta"))
        compare = compare[compare["valor_abs"] > compare["valor_meta"]]
        for _, row in compare.head(10).iterrows():
            observations.append(
                f"Em {row['competencia']}, a taxa de absenteísmo está acima da meta informada na aba de rotatividade para {row['area']}."
            )

    top_costs = (
        cost_df.groupby("categoria_custo", dropna=False)["valor"].sum().sort_values(ascending=False).head(5).reset_index()
        if not cost_df.empty
        else pd.DataFrame(columns=["categoria_custo", "valor"])
    )
    top_inconsistencies = pd.DataFrame(quality["validacoes"]).head(5) if quality["validacoes"] else pd.DataFrame()

    html_lines = [
        "<html><head><meta charset='utf-8'><title>Resumo Executivo RH</title></head><body>",
        "<h1>Resumo Executivo RH / Folha</h1>",
        "<h2>Principais KPIs</h2>",
        kpi_df.to_html(index=False),
        "<h2>Top 5 categorias de custo</h2>",
        top_costs.to_html(index=False),
        "<h2>Top 5 inconsistências</h2>",
        top_inconsistencies.to_html(index=False) if not top_inconsistencies.empty else "<p>Sem inconsistências adicionais.</p>",
        "<h2>Observações automáticas</h2>",
        "<ul>",
    ]
    if observations:
        html_lines.extend([f"<li>{item}</li>" for item in observations[:10]])
    else:
        html_lines.append("<li>Não foram identificadas ocorrências acima de meta com base disponível.</li>")
    html_lines.extend(["</ul>", "</body></html>"])
    (REPORTS_DIR / "resumo_executivo.html").write_text("\n".join(html_lines), encoding="utf-8")

    with pd.ExcelWriter(REPORTS_DIR / "resumo_executivo.xlsx", engine="xlsxwriter") as writer:
        kpi_df.to_excel(writer, sheet_name="KPIs", index=False)
        top_costs.to_excel(writer, sheet_name="Top Custos", index=False)
        pd.DataFrame({"observacoes": observations or ["Sem observações acima de meta."]}).to_excel(
            writer, sheet_name="Observacoes", index=False
        )
        if not top_inconsistencies.empty:
            top_inconsistencies.to_excel(writer, sheet_name="Qualidade", index=False)


def main() -> None:
    ensure_directories()
    stage_raw_files()

    catalog_df, error_df = build_catalog(RAW_DIR)
    catalog_df.to_csv(PROCESSED_DIR / "catalogo_abas.csv", index=False, encoding="utf-8-sig")
    error_df.to_csv(PROCESSED_DIR / "erros_celulas.csv", index=False, encoding="utf-8-sig")

    people = extract_people_dimensions(RAW_DIR)
    indicators = extract_indicator_facts(RAW_DIR)
    payroll = extract_payroll_facts(RAW_DIR)
    if not people["fato_folha_base"].empty:
        payroll = pd.concat([payroll, people["fato_folha_base"]], ignore_index=True, sort=False)
    cost_df = extract_cost_facts(RAW_DIR)

    movimentacao = build_movimentacao(indicators)
    absenteismo = build_absenteismo(indicators)
    indicators = append_calculated_indicators(indicators, movimentacao)

    if not cost_df.empty:
        extras = []
        grouped_cost = cost_df.groupby(["periodo_id", "area", "subarea"], dropna=False).agg(
            custo_total=("custo_total", "max"),
            percentual_custo=("percentual_custo_faturamento", "max"),
            faturamento_colaborador=("faturamento_por_colaborador", "max"),
            origem_arquivo=("origem_arquivo", "first"),
            origem_aba=("origem_aba", "first"),
        )
        for idx, row in grouped_cost.reset_index().iterrows():
            ano = int(str(row["periodo_id"])[:4])
            mes_num = int(str(row["periodo_id"])[5:7])
            extras.extend(
                [
                    {
                        "periodo_id": row["periodo_id"],
                        "ano": ano,
                        "mes_num": mes_num,
                        "mes": None,
                        "competencia": row["periodo_id"],
                        "area": row["area"],
                        "subarea": row["subarea"],
                        "indicador": "Custo Total",
                        "valor": row["custo_total"],
                        "unidade": "R$",
                        "origem_arquivo": row["origem_arquivo"],
                        "origem_aba": row["origem_aba"],
                        "origem_range": "agregado_de_custo_fopag",
                        "confiabilidade": confidence_label(False),
                        "formula_origem": None,
                    },
                    {
                        "periodo_id": row["periodo_id"],
                        "ano": ano,
                        "mes_num": mes_num,
                        "mes": None,
                        "competencia": row["periodo_id"],
                        "area": row["area"],
                        "subarea": row["subarea"],
                        "indicador": "Custo / Faturamento %",
                        "valor": row["percentual_custo"],
                        "unidade": "%",
                        "origem_arquivo": row["origem_arquivo"],
                        "origem_aba": row["origem_aba"],
                        "origem_range": "agregado_de_custo_fopag",
                        "confiabilidade": confidence_label(False),
                        "formula_origem": None,
                    },
                    {
                        "periodo_id": row["periodo_id"],
                        "ano": ano,
                        "mes_num": mes_num,
                        "mes": None,
                        "competencia": row["periodo_id"],
                        "area": row["area"],
                        "subarea": row["subarea"],
                        "indicador": "Faturamento por Colaborador",
                        "valor": row["faturamento_colaborador"],
                        "unidade": "R$",
                        "origem_arquivo": row["origem_arquivo"],
                        "origem_aba": row["origem_aba"],
                        "origem_range": "agregado_de_custo_fopag",
                        "confiabilidade": confidence_label(False),
                        "formula_origem": None,
                    },
                ]
            )
        indicators = pd.concat([indicators, pd.DataFrame(extras)], ignore_index=True, sort=False)

    period_seed = []
    for df, period_col in [
        (indicators, "periodo_id"),
        (payroll, "periodo_id"),
        (cost_df, "periodo_id"),
        (people["fato_beneficios"], "periodo_id"),
    ]:
        if df is None or df.empty:
            continue
        for value in df[period_col].dropna().unique():
            year = int(str(value)[:4])
            month = int(str(value)[5:7])
            period_seed.append(
                {
                    "ano": year,
                    "mes_num": month,
                    "mes_nome": {
                        1: "Janeiro",
                        2: "Fevereiro",
                        3: "Março",
                        4: "Abril",
                        5: "Maio",
                        6: "Junho",
                        7: "Julho",
                        8: "Agosto",
                        9: "Setembro",
                        10: "Outubro",
                        11: "Novembro",
                        12: "Dezembro",
                    }[month],
                    "competencia": value,
                }
            )
    dim_periodo = build_period_dimension(period_seed)
    dim_area = build_dim_area(indicators, payroll, cost_df, movimentacao, absenteismo)

    quality = build_data_quality(catalog_df, error_df, people["dim_colaborador"], cost_df, movimentacao, indicators)
    write_quality_reports(REPORTS_DIR, quality)
    build_executive_reports(indicators, cost_df, quality)
    (REPORTS_DIR / "dicionario_metricas.md").write_text(build_metric_dictionary(), encoding="utf-8")

    save_dataset(dim_periodo, "dim_periodo")
    save_dataset(dim_area, "dim_area")
    save_dataset(people["dim_colaborador"], "dim_colaborador")
    save_dataset(indicators, "fato_indicadores_mensais")
    save_dataset(payroll, "fato_folha_mensal")
    save_dataset(cost_df, "fato_custo_mensal")
    save_dataset(movimentacao, "fato_movimentacao")
    save_dataset(absenteismo, "fato_absenteismo")
    save_dataset(people["fato_beneficios"], "fato_beneficios")
    save_dataset(people["fato_desligamentos"], "fato_desligamentos")

    print("Pipeline concluído.")
    print(f"Arquivos processados em: {PROCESSED_DIR}")
    print(f"Relatórios em: {REPORTS_DIR}")


if __name__ == "__main__":
    main()
