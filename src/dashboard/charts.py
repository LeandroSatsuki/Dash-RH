from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _source_note(df: pd.DataFrame) -> str:
    if df.empty:
        return "Fonte: sem dados"
    files = sorted(set(df.get("origem_arquivo", [])))
    labels = ", ".join(files[:2])
    if len(files) > 2:
        labels += "..."
    return f"Fonte: {labels}"


def line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str | None,
    title: str,
    y_title: str,
    tickformat: str | None = None,
) -> go.Figure:
    fig = px.line(df, x=x, y=y, color=color, markers=True, custom_data=["origem_aba", "confiabilidade"])
    fig.update_traces(
        hovertemplate="%{x}<br>Valor=%{y}<br>Aba=%{customdata[0]}<br>Status=%{customdata[1]}<extra></extra>"
    )
    fig.update_layout(title=title, xaxis_title="Competência", yaxis_title=y_title, legend_title_text="")
    if tickformat:
        fig.update_yaxes(tickformat=tickformat)
    fig.add_annotation(
        x=1,
        y=-0.18,
        xref="paper",
        yref="paper",
        text=_source_note(df),
        showarrow=False,
        xanchor="right",
    )
    return fig


def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str | None,
    title: str,
    y_title: str,
    barmode: str = "group",
    tickformat: str | None = None,
) -> go.Figure:
    fig = px.bar(df, x=x, y=y, color=color, barmode=barmode, custom_data=["origem_aba", "confiabilidade"])
    fig.update_traces(
        hovertemplate="%{x}<br>Valor=%{y}<br>Aba=%{customdata[0]}<br>Status=%{customdata[1]}<extra></extra>"
    )
    fig.update_layout(title=title, xaxis_title="Competência", yaxis_title=y_title, legend_title_text="")
    if tickformat:
        fig.update_yaxes(tickformat=tickformat)
    fig.add_annotation(
        x=1,
        y=-0.18,
        xref="paper",
        yref="paper",
        text=_source_note(df),
        showarrow=False,
        xanchor="right",
    )
    return fig


def heatmap(df: pd.DataFrame, x: str, y: str, z: str, title: str) -> go.Figure:
    pivot = df.pivot_table(index=y, columns=x, values=z, aggfunc="mean")
    fig = px.imshow(pivot, text_auto=".2%", aspect="auto", color_continuous_scale="YlOrRd")
    fig.update_layout(title=title, xaxis_title="Competência", yaxis_title="Área/Subárea")
    fig.add_annotation(x=1, y=-0.18, xref="paper", yref="paper", text=_source_note(df), showarrow=False, xanchor="right")
    return fig


def pareto_chart(df: pd.DataFrame, category_col: str, value_col: str, title: str) -> go.Figure:
    chart_df = df.groupby(category_col, dropna=False)[value_col].sum().sort_values(ascending=False).reset_index()
    chart_df["percentual_acumulado"] = chart_df[value_col].cumsum() / chart_df[value_col].sum()
    fig = go.Figure()
    fig.add_bar(x=chart_df[category_col], y=chart_df[value_col], name="Valor")
    fig.add_scatter(
        x=chart_df[category_col],
        y=chart_df["percentual_acumulado"],
        yaxis="y2",
        name="% acumulado",
        mode="lines+markers",
    )
    fig.update_layout(
        title=title,
        xaxis_title="Categoria",
        yaxis_title="Valor (R$)",
        yaxis2=dict(overlaying="y", side="right", tickformat=".0%"),
    )
    fig.add_annotation(x=1, y=-0.18, xref="paper", yref="paper", text=_source_note(df), showarrow=False, xanchor="right")
    return fig


def scatter_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    size: str,
    color: str,
    title: str,
) -> go.Figure:
    fig = px.scatter(df, x=x, y=y, size=size, color=color, hover_name="periodo_id")
    fig.update_layout(title=title, xaxis_title=x, yaxis_title=y)
    fig.add_annotation(x=1, y=-0.18, xref="paper", yref="paper", text=_source_note(df), showarrow=False, xanchor="right")
    return fig


def table_figure(df: pd.DataFrame, title: str) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=list(df.columns)),
                cells=dict(values=[df[column].tolist() for column in df.columns]),
            )
        ]
    )
    fig.update_layout(title=title)
    return fig

