from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud import ponto as crud_ponto
from src.db.models import Colaborador, Importacao
from src.services.audit_service import log_action
from src.utils.logging_config import configure_logging, log_structured

SUPPORTED_COLUMNS = {"matricula", "cpf", "nome", "data", "entrada", "saida_intervalo", "retorno_intervalo", "saida"}
logger = configure_logging("importacao_ponto")


@dataclass
class ImportacaoPontoResultado:
    total_linhas: int
    importadas: int
    erros: list[dict[str, Any]]


def carregar_arquivo(path: str | Path) -> pd.DataFrame:
    target = Path(path)
    if target.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(target)
    return pd.read_csv(target)


def preview_importacao(path: str | Path, limit: int = 20) -> list[dict[str, Any]]:
    df = carregar_arquivo(path)
    return df.head(limit).to_dict(orient="records")


def importar_marcacoes(
    db: Session,
    *,
    path: str | Path,
    column_map: dict[str, str],
    usuario_id: int | None = None,
    origem: str = "importado_csv",
    sobrescrever_manual: bool = False,
) -> ImportacaoPontoResultado:
    log_structured(logger, 20, "inicio importacao de ponto", arquivo=str(path), origem=origem, usuario_id=usuario_id)
    df = carregar_arquivo(path)
    erros: list[dict[str, Any]] = []
    importadas = 0
    importacao = Importacao(
        nome_arquivo=Path(path).name,
        tipo_importacao="ponto",
        status="processando",
        total_linhas=len(df.index),
        usuario_id=usuario_id,
    )
    db.add(importacao)
    db.commit()
    db.refresh(importacao)
    for idx, row in df.iterrows():
        try:
            colaborador = _resolver_colaborador(db, row, column_map)
            data_ref = _value(row, column_map, "data")
            for tipo in ["entrada", "saida_intervalo", "retorno_intervalo", "saida"]:
                horario = _value(row, column_map, tipo)
                if horario in (None, "", float("nan")):
                    continue
                if not sobrescrever_manual and _marcacao_existente(db, colaborador.id, data_ref, tipo, horario):
                    raise ValueError(f"Marcacao duplicada encontrada para {tipo}.")
                crud_ponto.criar_marcacao(
                    db,
                    {
                        "colaborador_id": colaborador.id,
                        "data": data_ref,
                        "tipo": tipo,
                        "horario": horario,
                        "origem": origem,
                        "observacao": f"Importado de {Path(path).name}",
                    },
                    usuario_id,
                )
            importadas += 1
        except Exception as exc:
            erros.append({"linha": int(idx) + 2, "erro": str(exc)})
    importacao.status = "concluida" if not erros else "concluida_com_erros"
    importacao.linhas_importadas = importadas
    importacao.linhas_com_erro = len(erros)
    importacao.relatorio_erros = {"erros": erros}
    db.add(importacao)
    db.commit()
    db.refresh(importacao)
    log_action(
        db,
        tabela="importacoes",
        acao="importacao_ponto",
        registro_id=importacao.id,
        usuario_id=usuario_id,
        origem="ponto",
        valor_novo={"arquivo": importacao.nome_arquivo, "importadas": importadas, "erros": len(erros)},
    )
    log_structured(logger, 20, "fim importacao de ponto", arquivo=str(path), importadas=importadas, erros=len(erros))
    return ImportacaoPontoResultado(total_linhas=len(df.index), importadas=importadas, erros=erros)


def _value(row, column_map: dict[str, str], field: str):
    column_name = column_map.get(field)
    if not column_name:
        return None
    if column_name not in row.index:
        raise ValueError(f"Coluna mapeada ausente: {column_name}")
    value = row[column_name]
    if pd.isna(value):
        return None
    if field == "data" and not isinstance(value, date):
        try:
            return pd.to_datetime(value).date()
        except Exception as exc:
            raise ValueError("Data de marcacao invalida.") from exc
    if field in {"entrada", "saida_intervalo", "retorno_intervalo", "saida"}:
        if hasattr(value, "to_pydatetime"):
            return value.to_pydatetime().time()
        if hasattr(value, "time"):
            return value.time()
        return str(value)
    return value


def _resolver_colaborador(db: Session, row, column_map: dict[str, str]) -> Colaborador:
    matricula = _value(row, column_map, "matricula")
    cpf = _value(row, column_map, "cpf")
    nome = _value(row, column_map, "nome")
    if matricula:
        colaborador = db.scalar(select(Colaborador).where(Colaborador.matricula == str(matricula), Colaborador.deletado_em.is_(None)))
        if colaborador:
            return colaborador
    if cpf:
        colaborador = db.scalar(select(Colaborador).where(Colaborador.cpf == str(cpf), Colaborador.deletado_em.is_(None)))
        if colaborador:
            return colaborador
    if nome:
        colaborador = db.scalar(select(Colaborador).where(Colaborador.nome_completo == str(nome), Colaborador.deletado_em.is_(None)))
        if colaborador:
            return colaborador
    raise ValueError("Colaborador nao encontrado para a linha importada.")


def _marcacao_existente(db: Session, colaborador_id: int, data_ref: date, tipo: str, horario) -> bool:
    existentes = crud_ponto.listar_marcacoes(db, colaborador_id=colaborador_id, data_inicio=data_ref, data_fim=data_ref)
    horario_norm = str(horario)
    return any(item.tipo == tipo and item.horario.isoformat() == horario_norm for item in existentes)
