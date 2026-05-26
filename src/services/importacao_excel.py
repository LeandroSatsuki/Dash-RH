from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud import afastamentos as crud_afastamentos
from src.crud import beneficios as crud_beneficios
from src.crud import colaboradores as crud_colaboradores
from src.db.models import Colaborador, Importacao
from src.extract.read_excel import worksheet_to_table
from src.services.auditoria import registrar_auditoria
from src.utils.excel_dates import competencia_from_date, convert_excel_date
from src.utils.numbers import to_number


def _registrar_importacao(
    db: Session,
    nome_arquivo: str,
    tipo_importacao: str,
    status: str,
    total_linhas: int,
    linhas_importadas: int,
    linhas_com_erro: int,
    relatorio_erros: list[dict],
    usuario_id: int | None = None,
) -> Importacao:
    registro = Importacao(
        nome_arquivo=nome_arquivo,
        tipo_importacao=tipo_importacao,
        status=status,
        total_linhas=total_linhas,
        linhas_importadas=linhas_importadas,
        linhas_com_erro=linhas_com_erro,
        relatorio_erros={"erros": relatorio_erros},
        usuario_id=usuario_id,
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


def importar_colaboradores_cadastro(db: Session, file_path: str | Path, usuario_id: int | None = None) -> dict:
    rows = worksheet_to_table(file_path, "Cadastro", header_row=1)
    erros = []
    importados = 0
    for row in rows:
        cpf = row.get("CPF")
        matricula = row.get("ID_Colaborador")
        existente = db.scalar(
            select(Colaborador).where((Colaborador.cpf == str(cpf)) | (Colaborador.matricula == str(matricula)))
        )
        if existente:
            continue
        try:
            crud_colaboradores.criar(
                db,
                {
                    "matricula": str(matricula) if matricula is not None else None,
                    "nome_completo": row.get("Nome_RazaoSocial") or "Sem nome",
                    "cpf": str(cpf) if cpf is not None else None,
                    "email": row.get("Email"),
                    "telefone": row.get("Telefone"),
                    "regime_contratual": row.get("Regime_Contratual"),
                    "data_admissao": convert_excel_date(row.get("Data_Admissao")),
                    "status": "ativo" if row.get("Data_Desligamento") in (None, "") else "desligado",
                    "data_desligamento": convert_excel_date(row.get("Data_Desligamento")),
                    "origem": "importado_excel",
                },
                usuario_id,
            )
            importados += 1
        except Exception as exc:
            erros.append({"linha": importados + len(erros) + 1, "erro": str(exc)})
    _registrar_importacao(db, Path(file_path).name, "cadastro", "concluida", len(rows), importados, len(erros), erros, usuario_id)
    return {"total_linhas": len(rows), "linhas_importadas": importados, "linhas_com_erro": len(erros), "erros": erros}


def importar_afastamentos(db: Session, file_path: str | Path, usuario_id: int | None = None) -> dict:
    rows = worksheet_to_table(file_path, "TB_Afastamentos", header_row=1)
    erros = []
    importados = 0
    for idx, row in enumerate(rows, start=1):
        try:
            colaborador = db.scalar(select(Colaborador).where(Colaborador.matricula == str(row.get("ID_Colaborador"))))
            if colaborador is None:
                erros.append({"linha": idx, "erro": "Colaborador não encontrado"})
                continue
            crud_afastamentos.criar(
                db,
                {
                    "colaborador_id": colaborador.id,
                    "tipo": row.get("Tipo_Afastamento") or "outros",
                    "data_inicio": convert_excel_date(row.get("Data_Inicio")),
                    "data_fim": convert_excel_date(row.get("Data_Fim")),
                    "quantidade_dias": to_number(row.get("Quantidade_Dias")),
                    "quantidade_horas": to_number(row.get("Quantidade_Horas")),
                    "impacta_folha": True,
                    "impacta_absenteismo": True,
                    "cid_mascarado": row.get("CID"),
                    "status": "ativo",
                    "observacao": "Importado de planilha",
                },
                usuario_id,
            )
            importados += 1
        except Exception as exc:
            erros.append({"linha": idx, "erro": str(exc)})
    _registrar_importacao(db, Path(file_path).name, "afastamentos", "concluida", len(rows), importados, len(erros), erros, usuario_id)
    return {"total_linhas": len(rows), "linhas_importadas": importados, "linhas_com_erro": len(erros), "erros": erros}


def importar_beneficios(db: Session, file_path: str | Path, usuario_id: int | None = None) -> dict:
    rows = worksheet_to_table(file_path, "TB_Elegibilidade", header_row=1)
    erros = []
    importados = 0
    for idx, row in enumerate(rows, start=1):
        colaborador = db.scalar(select(Colaborador).where(Colaborador.matricula == str(row.get("ID_Colaborador"))))
        if colaborador is None:
            erros.append({"linha": idx, "erro": "Colaborador não encontrado"})
            continue
        for nome, status in {
            "VR": row.get("Status_VR"),
            "VA": row.get("Status_VA"),
            "VT": row.get("Status_VT"),
        }.items():
            if status in (None, "", "Não"):
                continue
            beneficio = next((item for item in crud_beneficios.listar(db) if item.nome == nome), None)
            if beneficio is None:
                beneficio = crud_beneficios.criar(db, {"nome": nome, "tipo": "beneficio", "status": "ativo"}, usuario_id)
            crud_beneficios.vincular_ao_colaborador(
                db,
                {
                    "colaborador_id": colaborador.id,
                    "beneficio_id": beneficio.id,
                    "status": "ativo",
                    "observacao": "Importado de planilha",
                },
                usuario_id,
            )
            importados += 1
    _registrar_importacao(db, Path(file_path).name, "beneficios", "concluida", len(rows), importados, len(erros), erros, usuario_id)
    return {"total_linhas": len(rows), "linhas_importadas": importados, "linhas_com_erro": len(erros), "erros": erros}


def importar_desligamentos(db: Session, file_path: str | Path, usuario_id: int | None = None) -> dict:
    rows = worksheet_to_table(file_path, "TB_Desligamentos", header_row=1)
    erros = []
    atualizados = 0
    for idx, row in enumerate(rows, start=1):
        colaborador = db.scalar(select(Colaborador).where(Colaborador.matricula == str(row.get("ID_Colaborador"))))
        if colaborador is None:
            erros.append({"linha": idx, "erro": "Colaborador não encontrado"})
            continue
        colaborador.status = "desligado"
        colaborador.data_desligamento = convert_excel_date(row.get("Data_Desligamento"))
        db.add(colaborador)
        db.commit()
        atualizados += 1
    _registrar_importacao(db, Path(file_path).name, "desligamentos", "concluida", len(rows), atualizados, len(erros), erros, usuario_id)
    return {"total_linhas": len(rows), "linhas_importadas": atualizados, "linhas_com_erro": len(erros), "erros": erros}


def importar_arquivo_legado(db: Session, file_path: str | Path, usuario_id: int | None = None) -> dict:
    path = Path(file_path)
    resultado = {
        "arquivo": path.name,
        "cadastro": importar_colaboradores_cadastro(db, path, usuario_id),
    }
    try:
        resultado["afastamentos"] = importar_afastamentos(db, path, usuario_id)
    except Exception as exc:
        resultado["afastamentos"] = {"erro": str(exc)}
    try:
        resultado["beneficios"] = importar_beneficios(db, path, usuario_id)
    except Exception as exc:
        resultado["beneficios"] = {"erro": str(exc)}
    try:
        resultado["desligamentos"] = importar_desligamentos(db, path, usuario_id)
    except Exception as exc:
        resultado["desligamentos"] = {"erro": str(exc)}
    registrar_auditoria(db, "importacoes", "processar_excel", origem="importacao_excel", valor_novo=resultado, usuario_id=usuario_id)
    return resultado
