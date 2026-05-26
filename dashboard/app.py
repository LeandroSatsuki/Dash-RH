from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.dashboard.charts import bar_chart, heatmap, line_chart, pareto_chart, scatter_chart, table_figure
from src.utils.numbers import ensure_numeric_columns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

DATASET_NUMERIC_COLUMNS = {
    "fato_indicadores_mensais": ["ano", "mes_num", "valor"],
    "fato_movimentacao": ["admissoes", "desligamentos", "efetivo_inicial", "efetivo_final", "efetivo_medio", "turnover"],
    "fato_absenteismo": [
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
    ],
    "fato_custo_mensal": [
        "valor",
        "faturamento",
        "custo_total",
        "percentual_custo_faturamento",
        "meta",
        "colaboradores",
        "faturamento_por_colaborador",
    ],
    "fato_folha_mensal": [
        "salario",
        "premios",
        "ajuda_custo",
        "alimentacao",
        "plano_saude",
        "beneficios",
        "encargos_inss",
        "fgts",
        "provisoes",
        "total_geral",
        "percentual_custo",
        "faturamento_referencia",
    ],
}


def load_dataset(name: str) -> pd.DataFrame:
    parquet_path = PROCESSED_DIR / f"{name}.parquet"
    csv_path = PROCESSED_DIR / f"{name}.csv"
    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
        return ensure_numeric_columns(df, DATASET_NUMERIC_COLUMNS.get(name, []))
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        return ensure_numeric_columns(df, DATASET_NUMERIC_COLUMNS.get(name, []))
    return pd.DataFrame()


def apply_filters(df: pd.DataFrame, years, months, areas, subareas) -> pd.DataFrame:
    if df.empty:
        return df
    filtered = df.copy()
    if years:
        if "ano" in filtered.columns:
            filtered = filtered[filtered["ano"].isin(years)]
        elif "periodo_id" in filtered.columns:
            filtered = filtered[filtered["periodo_id"].str[:4].astype(int).isin(years)]
    if months and "mes_num" in filtered.columns:
        filtered = filtered[filtered["mes_num"].isin(months)]
    if areas and "area" in filtered.columns:
        filtered = filtered[filtered["area"].isin(areas)]
    if subareas and "subarea" in filtered.columns:
        filtered = filtered[filtered["subarea"].fillna("").isin(subareas)]
    return filtered


def latest_metric(df: pd.DataFrame, indicator: str):
    subset = df[df["indicador"].eq(indicator) & df["valor"].notna()].sort_values(["competencia", "area", "subarea"])
    if subset.empty:
        return None, None, None
    current = subset.iloc[-1]
    previous = subset.iloc[-2]["valor"] if len(subset) > 1 else None
    delta = current["valor"] - previous if previous is not None and current["valor"] is not None else None
    alert = current["confiabilidade"] == "Dado pendente / inconsistente"
    return current["valor"], delta, alert


def fmt_money(value):
    return "R$ -" if value is None or pd.isna(value) else f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(value):
    return "-" if value is None or pd.isna(value) else f"{value:.2%}"


def fmt_num(value):
    return "-" if value is None or pd.isna(value) else f"{value:,.0f}".replace(",", ".")


def executive_page(indicators: pd.DataFrame, cost_df: pd.DataFrame):
    indicators = ensure_numeric_columns(indicators, ["valor"])
    st.subheader("Visão Executiva")
    cols = st.columns(5)
    metrics = [
        ("Efetivo Final (Un)", fmt_num),
        ("Efetivo Médio", fmt_num),
        ("Admissões", fmt_num),
        ("Desligamentos", fmt_num),
        ("Turnover", fmt_pct),
        ("Taxa de Absenteísmo", fmt_pct),
        ("Folha Bruta (R$)", fmt_money),
        ("Custo Total", fmt_money),
        ("Custo / Faturamento %", fmt_pct),
        ("Faturamento por Colaborador", fmt_money),
    ]
    for idx, (metric, formatter) in enumerate(metrics):
        value, delta, alert = latest_metric(indicators, metric)
        cols[idx % 5].metric(metric, formatter(value), delta=None if delta is None else round(delta, 4))
        if alert:
            cols[idx % 5].caption("Alerta: dado pendente / inconsistente")

    if not indicators.empty:
        timeline = indicators[indicators["indicador"].isin(["Turnover", "Taxa de Absenteísmo", "Folha Bruta (R$)", "Custo Total"])]
        timeline = timeline.sort_values(["competencia", "indicador"])
        st.plotly_chart(line_chart(timeline, "competencia", "valor", "indicador", "KPIs Mensais", "Valor"), use_container_width=True)
        st.dataframe(
            timeline[["competencia", "area", "subarea", "indicador", "valor", "confiabilidade"]].sort_values(
                ["competencia", "area", "indicador"]
            ),
            use_container_width=True,
        )


def headcount_page(mov_df: pd.DataFrame, indicators: pd.DataFrame):
    mov_df = ensure_numeric_columns(
        mov_df,
        ["admissoes", "desligamentos", "efetivo_inicial", "efetivo_final", "efetivo_medio", "turnover"],
    )
    indicators = ensure_numeric_columns(indicators, ["valor"])
    st.subheader("Headcount e Movimentação")
    if mov_df.empty:
        st.info("Sem dados de movimentação.")
        return
    long = mov_df.melt(
        id_vars=["periodo_id", "area", "subarea", "origem_arquivo", "origem_aba"],
        value_vars=["efetivo_inicial", "efetivo_final", "efetivo_medio"],
        var_name="indicador",
        value_name="valor",
    )
    long["confiabilidade"] = "extraido"
    st.plotly_chart(line_chart(long, "periodo_id", "valor", "indicador", "Linha mensal de efetivo", "Pessoas"), use_container_width=True)

    bar_df = mov_df.melt(
        id_vars=["periodo_id", "area", "subarea", "origem_arquivo", "origem_aba"],
        value_vars=["admissoes", "desligamentos"],
        var_name="indicador",
        value_name="valor",
    )
    bar_df["confiabilidade"] = "extraido"
    st.plotly_chart(bar_chart(bar_df, "periodo_id", "valor", "indicador", "Admissões x Desligamentos", "Pessoas"), use_container_width=True)

    mov_df["saldo_headcount"] = mov_df["admissoes"].fillna(0) - mov_df["desligamentos"].fillna(0)
    saldo = mov_df[["periodo_id", "saldo_headcount", "origem_aba"]].copy()
    saldo["confiabilidade"] = "calculado_pelo_pipeline"
    st.plotly_chart(line_chart(saldo, "periodo_id", "saldo_headcount", None, "Saldo de Headcount", "Pessoas"), use_container_width=True)

    meta = indicators[indicators["indicador"].eq("Meta Turnover")][["competencia", "valor"]].rename(columns={"competencia": "periodo_id", "valor": "meta"})
    table = mov_df.merge(meta, on="periodo_id", how="left")
    table["acima_meta"] = table["turnover"] > table["meta"]
    st.dataframe(table[["periodo_id", "area", "subarea", "efetivo_inicial", "efetivo_final", "admissoes", "desligamentos", "turnover", "meta", "acima_meta"]], use_container_width=True)


def absenteismo_page(abs_df: pd.DataFrame, indicators: pd.DataFrame):
    abs_df = ensure_numeric_columns(
        abs_df,
        [
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
        ],
    )
    indicators = ensure_numeric_columns(indicators, ["valor"])
    st.subheader("Absenteísmo")
    if abs_df.empty:
        st.info("Sem dados de absenteísmo.")
        return
    meta = indicators[indicators["indicador"].eq("Meta Absenteísmo")][["competencia", "valor"]].rename(columns={"competencia": "periodo_id", "valor": "meta"})
    chart = abs_df.merge(meta, on="periodo_id", how="left")
    chart_long = chart.melt(
        id_vars=["periodo_id", "area", "subarea", "origem_arquivo", "origem_aba"],
        value_vars=["taxa_absenteismo", "meta"],
        var_name="indicador",
        value_name="valor",
    )
    chart_long["confiabilidade"] = "extraido"
    st.plotly_chart(line_chart(chart_long, "periodo_id", "valor", "indicador", "Taxa de Absenteísmo x Meta", "%"), use_container_width=True)

    hours = abs_df.melt(
        id_vars=["periodo_id", "area", "subarea", "origem_arquivo", "origem_aba"],
        value_vars=["horas_programadas", "horas_nao_produtivas"],
        var_name="indicador",
        value_name="valor",
    )
    hours["confiabilidade"] = "extraido"
    st.plotly_chart(bar_chart(hours, "periodo_id", "valor", "indicador", "Horas Programadas x Não Produtivas", "Horas"), use_container_width=True)

    stacked = abs_df.melt(
        id_vars=["periodo_id", "area", "subarea", "origem_arquivo", "origem_aba"],
        value_vars=["afastamentos_dias", "faltas_dias", "ferias_dias"],
        var_name="indicador",
        value_name="valor",
    )
    stacked["confiabilidade"] = "extraido"
    st.plotly_chart(bar_chart(stacked, "periodo_id", "valor", "indicador", "Afastamentos, Faltas e Férias", "Dias", barmode="stack"), use_container_width=True)

    heat_df = abs_df.copy()
    heat_df["area_subarea"] = heat_df["subarea"].fillna(heat_df["area"])
    st.plotly_chart(heatmap(heat_df, "periodo_id", "area_subarea", "taxa_absenteismo", "Heatmap de Absenteísmo"), use_container_width=True)

    ranking = heat_df.groupby("area_subarea", dropna=False)["taxa_absenteismo"].mean().sort_values(ascending=False).reset_index()
    st.dataframe(ranking, use_container_width=True)


def folha_custo_page(indicators: pd.DataFrame, cost_df: pd.DataFrame):
    indicators = ensure_numeric_columns(indicators, ["valor"])
    cost_df = ensure_numeric_columns(
        cost_df,
        ["valor", "faturamento", "custo_total", "percentual_custo_faturamento", "meta", "colaboradores", "faturamento_por_colaborador"],
    )
    st.subheader("Folha e Custo")
    folha = indicators[indicators["indicador"].isin(["Folha Bruta (R$)", "Folha Líquida (R$)", "Custo Total"])].copy()
    if not folha.empty:
        st.plotly_chart(line_chart(folha, "competencia", "valor", "indicador", "Folha Bruta, Líquida e Custo Total", "R$"), use_container_width=True)
    if not cost_df.empty:
        cost_df = cost_df.copy()
        cost_df["confiabilidade"] = "extraido"
        st.plotly_chart(bar_chart(cost_df, "periodo_id", "valor", "categoria_custo", "Custo por Categoria", "R$", barmode="stack"), use_container_width=True)
        st.plotly_chart(pareto_chart(cost_df, "categoria_custo", "valor", "Pareto de Categorias de Custo"), use_container_width=True)
        ratio = cost_df.groupby(["periodo_id", "area", "subarea"], dropna=False).agg(
            percentual=("percentual_custo_faturamento", "max"),
            meta=("meta", "max"),
            faturamento_por_colaborador=("faturamento_por_colaborador", "max"),
            custo_total=("custo_total", "max"),
            faturamento=("faturamento", "max"),
            colaboradores=("colaboradores", "max"),
            origem_aba=("origem_aba", "first"),
        ).reset_index()
        ratio["confiabilidade"] = "extraido"
        ratio_long = ratio.melt(
            id_vars=["periodo_id", "area", "subarea", "origem_aba", "confiabilidade"],
            value_vars=["percentual", "meta"],
            var_name="indicador",
            value_name="valor",
        )
        st.plotly_chart(line_chart(ratio_long, "periodo_id", "valor", "indicador", "Custo / Faturamento % x Meta", "%"), use_container_width=True)
        fat_colab = ratio[["periodo_id", "faturamento_por_colaborador", "origem_aba", "confiabilidade"]].rename(columns={"faturamento_por_colaborador": "valor"})
        st.plotly_chart(line_chart(fat_colab, "periodo_id", "valor", None, "Faturamento por Colaborador", "R$"), use_container_width=True)
        st.dataframe(cost_df[["periodo_id", "area", "subarea", "categoria_custo", "valor", "faturamento", "custo_total", "percentual_custo_faturamento"]], use_container_width=True)


def encargos_page(indicators: pd.DataFrame):
    indicators = ensure_numeric_columns(indicators, ["valor"])
    st.subheader("Encargos e Tributos")
    enc = indicators[indicators["indicador"].isin(["FGTS", "INSS Patronal", "Valor de Tributos", "Encargos sobre a Folha (%)"])].copy()
    if enc.empty:
        st.info("Sem dados de encargos.")
        return
    st.plotly_chart(line_chart(enc[enc["indicador"].isin(["FGTS", "INSS Patronal", "Valor de Tributos"])], "competencia", "valor", "indicador", "FGTS, INSS e Tributos", "R$"), use_container_width=True)
    pct = enc[enc["indicador"].eq("Encargos sobre a Folha (%)")]
    st.plotly_chart(line_chart(pct, "competencia", "valor", "area", "Encargos sobre a Folha %", "%"), use_container_width=True)
    compare = enc.groupby(["area", "indicador"], dropna=False)["valor"].sum().reset_index()
    compare["origem_aba"] = "Agregado"
    compare["confiabilidade"] = "extraido"
    st.plotly_chart(bar_chart(compare, "area", "valor", "indicador", "Comparativo de Encargos por Área", "R$"), use_container_width=True)


def comercial_page(indicators: pd.DataFrame, cost_df: pd.DataFrame):
    indicators = ensure_numeric_columns(indicators, ["valor"])
    cost_df = ensure_numeric_columns(
        cost_df,
        ["valor", "faturamento", "custo_total", "percentual_custo_faturamento", "meta", "colaboradores", "faturamento_por_colaborador"],
    )
    st.subheader("Comercial")
    commercial = indicators[indicators["area"].isin(["Comercial", "Geral"])].copy()
    if commercial.empty:
        st.info("Sem dados comerciais.")
        return
    focus = commercial[
        commercial["indicador"].isin(
            ["Comissão (R$)", "DSR (R$)", "Hora Extra (horas)", "Hora Extra + DSR (R$)", "Premiação CLT", "Premiação MEI"]
        )
    ]
    st.plotly_chart(line_chart(focus, "competencia", "valor", "indicador", "Indicadores Comerciais", "Valor"), use_container_width=True)
    compare = focus[focus["subarea"].notna()]
    if not compare.empty:
        st.plotly_chart(bar_chart(compare, "competencia", "valor", "subarea", "Comparativo entre Subáreas Comerciais", "Valor"), use_container_width=True)
    terceiros = cost_df[cost_df["categoria_custo"].astype(str).str.contains("MEI|FREELANCER|Terceiros", case=False, na=False)].copy()
    if not terceiros.empty:
        terceiros["confiabilidade"] = "extraido"
        st.plotly_chart(bar_chart(terceiros, "periodo_id", "valor", "categoria_custo", "Terceiros / MEI / Freelancer", "R$", barmode="stack"), use_container_width=True)
    ratio = cost_df[cost_df["area"].eq("Comercial")].groupby("periodo_id", dropna=False).agg(
        faturamento=("faturamento", "max"),
        custo_total=("custo_total", "max"),
        colaboradores=("colaboradores", "max"),
    ).reset_index()
    if not ratio.empty:
        ratio["area"] = "Comercial"
        st.plotly_chart(scatter_chart(ratio, "faturamento", "custo_total", "colaboradores", "area", "Faturamento x Custo Total"), use_container_width=True)


def fabril_page(indicators: pd.DataFrame, cost_df: pd.DataFrame):
    indicators = ensure_numeric_columns(indicators, ["valor"])
    cost_df = ensure_numeric_columns(
        cost_df,
        ["valor", "faturamento", "custo_total", "percentual_custo_faturamento", "meta", "colaboradores", "faturamento_por_colaborador"],
    )
    st.subheader("Fábrica / Fabril")
    fab = indicators[indicators["area"].eq("Fábrica")].copy()
    if fab.empty:
        st.info("Sem dados fabris.")
        return
    focus = fab[fab["indicador"].isin(["Efetivo Final (Un)", "Turnover", "Taxa de Absenteísmo", "Folha Bruta (R$)", "Custo Total"])]
    st.plotly_chart(line_chart(focus, "competencia", "valor", "indicador", "KPIs Fabris", "Valor"), use_container_width=True)
    fab_cost = cost_df[cost_df["area"].eq("Fábrica")].copy()
    if not fab_cost.empty:
        fab_cost["confiabilidade"] = "extraido"
        st.plotly_chart(bar_chart(fab_cost, "periodo_id", "valor", "categoria_custo", "Custo Fabril por Categoria", "R$", barmode="stack"), use_container_width=True)
        ratio = fab_cost.groupby("periodo_id").agg(percentual=("percentual_custo_faturamento", "max"), meta=("meta", "max")).reset_index()
        ratio["origem_aba"] = "Custo Fopag 26"
        ratio["confiabilidade"] = "extraido"
        ratio = ratio.melt(id_vars=["periodo_id", "origem_aba", "confiabilidade"], value_vars=["percentual", "meta"], var_name="indicador", value_name="valor")
        st.plotly_chart(line_chart(ratio, "periodo_id", "valor", "indicador", "Custo / Faturamento % Fabril", "%"), use_container_width=True)
    inconsistent = fab[fab["confiabilidade"].eq("Dado pendente / inconsistente")]
    if not inconsistent.empty:
        st.warning("Há alertas de inconsistência em Fabril/Fopag. Consulte a página de Qualidade dos Dados.")
        st.dataframe(inconsistent[["competencia", "indicador", "valor", "origem_aba", "origem_range"]], use_container_width=True)


def quality_page(error_df: pd.DataFrame, quality: dict):
    st.subheader("Qualidade dos Dados")
    if not error_df.empty:
        by_file = error_df.groupby("arquivo").size().reset_index(name="total_erros")
        by_file["origem_aba"] = "qualidade"
        by_file["confiabilidade"] = "extraido"
        st.plotly_chart(bar_chart(by_file, "arquivo", "total_erros", None, "Total de Erros por Arquivo", "Erros"), use_container_width=True)
        by_sheet = error_df.groupby("aba").size().reset_index(name="total_erros")
        by_sheet["origem_aba"] = "qualidade"
        by_sheet["confiabilidade"] = "extraido"
        st.plotly_chart(bar_chart(by_sheet, "aba", "total_erros", None, "Total de Erros por Aba", "Erros"), use_container_width=True)
        st.dataframe(error_df, use_container_width=True)
    st.markdown("### Integridade")
    st.write(f"Nomes possivelmente duplicados: {len(quality.get('nomes_possivelmente_duplicados', []))}")
    st.write(f"Ativos com Data_Desligamento preenchida: {len(quality.get('ativos_com_data_desligamento', []))}")
    st.write(f"Inativos sem Data_Desligamento: {len(quality.get('inativos_sem_data_desligamento', []))}")
    st.write(f"CPF/CNPJ ausente: {len(quality.get('cpf_cnpj_ausente', []))}")
    st.write(f"Meses com faturamento ausente e custo preenchido: {len(quality.get('meses_custo_sem_faturamento', []))}")
    st.write(f"Meses com custo zerado e colaboradores ativos: {len(quality.get('meses_custo_zero_com_colaboradores', []))}")
    validations = pd.DataFrame(quality.get("validacoes", []))
    if not validations.empty:
        st.dataframe(validations, use_container_width=True)


def main():
    st.set_page_config(page_title="Dashboard RH / Folha", layout="wide")
    st.title("Dashboard Executivo de RH / Folha de Pagamento")

    indicators = load_dataset("fato_indicadores_mensais")
    mov_df = load_dataset("fato_movimentacao")
    abs_df = load_dataset("fato_absenteismo")
    cost_df = load_dataset("fato_custo_mensal")
    error_df = pd.read_csv(PROCESSED_DIR / "erros_celulas.csv") if (PROCESSED_DIR / "erros_celulas.csv").exists() else pd.DataFrame()
    quality = json.loads((REPORTS_DIR / "qualidade_dados.json").read_text(encoding="utf-8")) if (REPORTS_DIR / "qualidade_dados.json").exists() else {}

    if indicators.empty and mov_df.empty and abs_df.empty and cost_df.empty:
        st.error("Nenhum dado processado encontrado. Execute `python main.py` antes de abrir o dashboard.")
        return

    years = sorted(pd.Series(indicators.get("ano", pd.Series(dtype=int))).dropna().astype(int).unique().tolist())
    months = sorted(pd.Series(indicators.get("mes_num", pd.Series(dtype=int))).dropna().astype(int).unique().tolist())
    areas = sorted(pd.Series(indicators.get("area", pd.Series(dtype=str))).dropna().unique().tolist())
    subareas = sorted(pd.Series(indicators.get("subarea", pd.Series(dtype=str))).dropna().unique().tolist())

    with st.sidebar:
        st.header("Filtros")
        sel_years = st.multiselect("Ano", options=years, default=years[-1:] if years else [])
        sel_months = st.multiselect("Mês", options=months, default=months[-1:] if months else [])
        sel_areas = st.multiselect("Área", options=areas, default=areas)
        sel_subareas = st.multiselect("Subárea", options=subareas)
        page = st.radio(
            "Página",
            [
                "Visão Executiva",
                "Headcount e Movimentação",
                "Absenteísmo",
                "Folha e Custo",
                "Encargos e Tributos",
                "Comercial",
                "Fábrica/Fabril",
                "Qualidade dos Dados",
            ],
        )

    indicators = apply_filters(indicators, sel_years, sel_months, sel_areas, sel_subareas)
    mov_df = apply_filters(mov_df, sel_years, sel_months, sel_areas, sel_subareas)
    abs_df = apply_filters(abs_df, sel_years, sel_months, sel_areas, sel_subareas)
    cost_df = apply_filters(cost_df, sel_years, sel_months, sel_areas, sel_subareas)

    if page == "Visão Executiva":
        executive_page(indicators, cost_df)
    elif page == "Headcount e Movimentação":
        headcount_page(mov_df, indicators)
    elif page == "Absenteísmo":
        absenteismo_page(abs_df, indicators)
    elif page == "Folha e Custo":
        folha_custo_page(indicators, cost_df)
    elif page == "Encargos e Tributos":
        encargos_page(indicators)
    elif page == "Comercial":
        comercial_page(indicators, cost_df)
    elif page == "Fábrica/Fabril":
        fabril_page(indicators, cost_df)
    elif page == "Qualidade dos Dados":
        quality_page(error_df, quality)


if __name__ == "__main__":
    main()
