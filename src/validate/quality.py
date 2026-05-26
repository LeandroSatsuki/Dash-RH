from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.numbers import ensure_numeric_columns
from src.utils.text import safe_divide


def _df_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []
    cleaned = df.copy()
    for column in cleaned.columns:
        if pd.api.types.is_datetime64_any_dtype(cleaned[column]):
            cleaned[column] = cleaned[column].dt.strftime("%Y-%m-%d")
    cleaned = cleaned.fillna("")
    records = cleaned.to_dict(orient="records")
    normalized = []
    for record in records:
        normalized.append({str(key): (value.isoformat() if hasattr(value, "isoformat") else value) for key, value in record.items()})
    return normalized


def build_data_quality(
    catalog_df: pd.DataFrame,
    error_df: pd.DataFrame,
    dim_colaborador: pd.DataFrame,
    fato_custo_mensal: pd.DataFrame,
    fato_movimentacao: pd.DataFrame,
    fato_indicadores_mensais: pd.DataFrame,
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    fato_indicadores_mensais = ensure_numeric_columns(fato_indicadores_mensais, ["valor"])
    fato_custo_mensal = ensure_numeric_columns(
        fato_custo_mensal, ["valor", "custo_total", "faturamento", "colaboradores"]
    )
    fato_movimentacao = ensure_numeric_columns(
        fato_movimentacao, ["efetivo_inicial", "efetivo_final", "admissoes", "desligamentos"]
    )

    if not fato_indicadores_mensais.empty:
        percent_df = fato_indicadores_mensais[
            fato_indicadores_mensais["unidade"].eq("%") & fato_indicadores_mensais["valor"].notna()
        ]
        invalid_pct = percent_df[(percent_df["valor"] < 0) | (percent_df["valor"] > 1)]
        for _, row in invalid_pct.iterrows():
            issues.append(
                {
                    "tipo": "percentual_fora_faixa",
                    "arquivo": row["origem_arquivo"],
                    "aba": row["origem_aba"],
                    "detalhe": f"{row['indicador']} em {row['competencia']} com valor {row['valor']}",
                }
            )

    if not fato_custo_mensal.empty:
        invalid_cost = fato_custo_mensal[fato_custo_mensal["valor"].fillna(0) < 0]
        for _, row in invalid_cost.iterrows():
            issues.append(
                {
                    "tipo": "custo_negativo",
                    "arquivo": row["origem_arquivo"],
                    "aba": row["origem_aba"],
                    "detalhe": f"{row['categoria_custo']} em {row['periodo_id']}",
                }
            )

    if not fato_movimentacao.empty:
        invalid_headcount = fato_movimentacao[
            (fato_movimentacao["efetivo_inicial"].fillna(0) < 0)
            | (fato_movimentacao["efetivo_final"].fillna(0) < 0)
            | (fato_movimentacao["admissoes"].fillna(0) < 0)
            | (fato_movimentacao["desligamentos"].fillna(0) < 0)
        ]
        for _, row in invalid_headcount.iterrows():
            issues.append(
                {
                    "tipo": "headcount_negativo",
                    "arquivo": row["origem_arquivo"],
                    "aba": row["origem_aba"],
                    "detalhe": f"{row['area']} {row['periodo_id']}",
                }
            )

    duplicated_names = (
        dim_colaborador.groupby("nome_razao_social", dropna=True)["id_colaborador"].nunique().reset_index(name="quantidade")
    )
    duplicated_names = duplicated_names[duplicated_names["quantidade"] > 1]

    ativos_com_desligamento = dim_colaborador[
        dim_colaborador["status"].eq("Ativo") & dim_colaborador["data_desligamento"].notna()
    ]
    inativos_sem_desligamento = dim_colaborador[
        dim_colaborador["status"].eq("Inativo") & dim_colaborador["data_desligamento"].isna()
    ]
    doc_ausente = dim_colaborador[
        dim_colaborador["cpf_mascarado"].isna() & dim_colaborador["cnpj_mascarado"].isna()
    ]

    meses_custo_sem_faturamento = pd.DataFrame()
    meses_custo_zero_com_colab = pd.DataFrame()
    if not fato_custo_mensal.empty:
        grouped = (
            fato_custo_mensal.groupby(["periodo_id", "area", "subarea"], dropna=False)
            .agg(
                custo_total=("custo_total", "max"),
                faturamento=("faturamento", "max"),
                colaboradores=("colaboradores", "max"),
            )
            .reset_index()
        )
        meses_custo_sem_faturamento = grouped[grouped["custo_total"].notna() & grouped["faturamento"].isna()]
        meses_custo_zero_com_colab = grouped[
            grouped["custo_total"].fillna(0).eq(0) & grouped["colaboradores"].fillna(0).gt(0)
        ]

    summary = {
        "total_erros_planilha": int(len(error_df)),
        "erros_por_arquivo": error_df.groupby("arquivo").size().to_dict() if not error_df.empty else {},
        "erros_por_aba": (
            {f"{arquivo} | {aba}": int(total) for (arquivo, aba), total in error_df.groupby(["arquivo", "aba"]).size().to_dict().items()}
            if not error_df.empty
            else {}
        ),
        "validacoes": issues,
        "nomes_possivelmente_duplicados": _df_to_records(duplicated_names),
        "ativos_com_data_desligamento": _df_to_records(ativos_com_desligamento),
        "inativos_sem_data_desligamento": _df_to_records(inativos_sem_desligamento),
        "cpf_cnpj_ausente": _df_to_records(doc_ausente),
        "meses_custo_sem_faturamento": _df_to_records(meses_custo_sem_faturamento),
        "meses_custo_zero_com_colaboradores": _df_to_records(meses_custo_zero_com_colab),
        "erros_celulas": _df_to_records(error_df),
    }
    return summary


def write_quality_reports(output_dir: str | Path, quality: dict[str, Any]) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "qualidade_dados.json"
    md_path = output_path / "qualidade_dados.md"
    json_path.write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Qualidade dos Dados",
        "",
        f"- Total de erros capturados em células: {quality['total_erros_planilha']}",
        f"- Arquivos com erro: {len(quality['erros_por_arquivo'])}",
        f"- Validações adicionais com alerta: {len(quality['validacoes'])}",
        "",
        "## Erros por arquivo",
    ]
    if quality["erros_por_arquivo"]:
        for arquivo, total in quality["erros_por_arquivo"].items():
            lines.append(f"- {arquivo}: {total}")
    else:
        lines.append("- Nenhum erro de fórmula identificado.")

    lines.extend(["", "## Top inconsistências", ""])
    top_issues = quality["validacoes"][:10]
    if top_issues:
        for issue in top_issues:
            lines.append(f"- {issue['tipo']}: {issue['detalhe']} ({issue['arquivo']} / {issue['aba']})")
    else:
        lines.append("- Nenhuma inconsistência adicional além dos erros de célula.")

    lines.extend(["", "## Dados ausentes / integridade", ""])
    lines.append(f"- Nomes possivelmente duplicados: {len(quality['nomes_possivelmente_duplicados'])}")
    lines.append(f"- Ativos com Data_Desligamento preenchida: {len(quality['ativos_com_data_desligamento'])}")
    lines.append(f"- Inativos sem Data_Desligamento: {len(quality['inativos_sem_data_desligamento'])}")
    lines.append(f"- CPF/CNPJ ausente: {len(quality['cpf_cnpj_ausente'])}")
    lines.append(f"- Meses com faturamento ausente e custo preenchido: {len(quality['meses_custo_sem_faturamento'])}")
    lines.append(
        f"- Meses com custo zerado e colaboradores ativos: {len(quality['meses_custo_zero_com_colaboradores'])}"
    )

    md_path.write_text("\n".join(lines), encoding="utf-8")
