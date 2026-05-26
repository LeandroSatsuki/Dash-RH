from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.extract.read_excel import worksheet_to_table
from src.utils.excel_dates import competencia_from_date, convert_excel_date
from src.utils.text import mask_document, mask_name, to_number


def _find_base_file(raw_dir: str | Path) -> Path:
    raw_path = Path(raw_dir)
    for file_path in raw_path.glob("*Folha de Pagamento Base.xlsx"):
        return file_path
    raise FileNotFoundError("Arquivo base não encontrado em data/raw.")


def extract_people_dimensions(raw_dir: str | Path) -> dict[str, pd.DataFrame]:
    file_path = _find_base_file(raw_dir)
    cadastro = pd.DataFrame(worksheet_to_table(file_path, "Cadastro", header_row=1))
    desligamentos = pd.DataFrame(worksheet_to_table(file_path, "TB_Desligamentos", header_row=1))
    elegibilidade = pd.DataFrame(worksheet_to_table(file_path, "TB_Elegibilidade", header_row=1))
    custo_folha = pd.DataFrame(worksheet_to_table(file_path, "TB_Custo_Folha", header_row=1))

    if not desligamentos.empty:
        desligamentos["Data_Desligamento"] = desligamentos["Data_Desligamento"].apply(convert_excel_date)
        desligamentos["Data_Aviso_Previo"] = desligamentos["Data_Aviso_Previo"].apply(convert_excel_date)

    desligamento_lookup = {}
    if not desligamentos.empty:
        desligamento_lookup = (
            desligamentos[["ID_Colaborador", "Data_Desligamento"]]
            .dropna(subset=["ID_Colaborador"])
            .drop_duplicates(subset=["ID_Colaborador"], keep="last")
            .set_index("ID_Colaborador")["Data_Desligamento"]
            .to_dict()
        )

    cadastro["Data_Admissao"] = cadastro["Data_Admissao"].apply(convert_excel_date)
    cadastro["Data_Desligamento"] = cadastro["ID_Colaborador"].map(desligamento_lookup)
    cadastro["Status"] = cadastro["Data_Desligamento"].apply(lambda value: "Inativo" if pd.notna(value) else "Ativo")

    dim_colaborador = pd.DataFrame(
        {
            "id_colaborador": cadastro["ID_Colaborador"],
            "nome_razao_social": cadastro["Nome_RazaoSocial"],
            "nome_mascarado": cadastro["Nome_RazaoSocial"].apply(mask_name),
            "regime_contratual": cadastro["Regime_Contratual"],
            "cargo_escopo": cadastro["Cargo_Escopo"],
            "departamento": cadastro["Departamento"],
            "status": cadastro["Status"],
            "data_admissao": cadastro["Data_Admissao"],
            "data_desligamento": cadastro["Data_Desligamento"],
            "cpf_mascarado": cadastro["CPF"].apply(mask_document),
            "cnpj_mascarado": cadastro["CNPJ"].apply(mask_document),
            "origem_arquivo": file_path.name,
            "origem_aba": "Cadastro",
        }
    )

    base_competencia = "2026-04"
    fato_beneficios = pd.DataFrame(
        {
            "id_colaborador": elegibilidade["ID_Colaborador"],
            "periodo_id": base_competencia,
            "status_vr": elegibilidade["Status_VR"],
            "status_va": elegibilidade["Status_VA"],
            "status_vt": elegibilidade["Status_VT"],
            "status_plano_saude_1": elegibilidade["Status_PlanoSaude_1"],
            "status_plano_saude_1_dep": elegibilidade["Status_PlanoSaude_1_dep"],
            "status_plano_saude_2": elegibilidade["Status_PlanoSaude_2"],
            "status_plano_saude_2_dep": elegibilidade["Status_PlanoSaude_2_dep"],
            "status_segvida": elegibilidade["Status_SegVida"],
            "status_segvida_dep": elegibilidade["Status_SegVida_dep"],
            "origem_arquivo": file_path.name,
            "origem_aba": "TB_Elegibilidade",
        }
    )

    fato_desligamentos = pd.DataFrame(
        {
            "id_colaborador": desligamentos.get("ID_Colaborador"),
            "nome_razao_social": desligamentos.get("Nome_RazaoSocial"),
            "data_aviso_previo": desligamentos.get("Data_Aviso_Previo"),
            "data_desligamento": desligamentos.get("Data_Desligamento"),
            "tipo_rescisao": desligamentos.get("Tipo_Rescisao"),
            "exame_demissional": desligamentos.get("Exame_Demissional"),
            "entrevista_realizada": desligamentos.get("Entrevista_Realizada"),
            "origem_arquivo": file_path.name,
            "origem_aba": "TB_Desligamentos",
        }
    )

    if not custo_folha.empty:
        custo_folha["Competencia"] = custo_folha["Competencia"].apply(convert_excel_date)
        fato_folha_base = pd.DataFrame(
            {
                "periodo_id": custo_folha["Competencia"].apply(competencia_from_date),
                "area": "Geral",
                "subarea": custo_folha["Departamento"],
                "colaborador": custo_folha["Nome_RazaoSocial"],
                "salario": custo_folha["Salario_Base"].apply(to_number),
                "premios": custo_folha["Premios"].apply(to_number),
                "ajuda_custo": custo_folha["Ajuda_Custo"].apply(to_number),
                "alimentacao": None,
                "plano_saude": None,
                "beneficios": custo_folha["Custo_Beneficios"].apply(to_number),
                "encargos_inss": custo_folha["Encargos_INSS"].apply(to_number),
                "fgts": custo_folha["Encargos_FGTS"].apply(to_number),
                "provisoes": custo_folha["Provisoes_Ferias_13"].apply(to_number),
                "total_geral": custo_folha["Custo_Total_Empresa"].apply(to_number),
                "percentual_custo": None,
                "faturamento_referencia": None,
                "origem_arquivo": file_path.name,
                "origem_aba": "TB_Custo_Folha",
            }
        )
    else:
        fato_folha_base = pd.DataFrame()

    return {
        "dim_colaborador": dim_colaborador,
        "fato_beneficios": fato_beneficios,
        "fato_desligamentos": fato_desligamentos,
        "fato_folha_base": fato_folha_base,
    }

