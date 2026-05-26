from __future__ import annotations

from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, soft_delete_record, update_record
from src.db.models import Colaborador
from src.services.validacoes_dp import (
    validar_cpf_obrigatorio_clt,
    validar_data_admissao_desligamento,
    validar_salario,
    validar_status_colaborador,
)
from src.utils.money import safe_decimal


def _validar(data: dict) -> None:
    if "salario_base" in data:
        data["salario_base"] = safe_decimal(data.get("salario_base"))
    validar_cpf_obrigatorio_clt(data.get("regime_contratual"), data.get("cpf"))
    validar_data_admissao_desligamento(data.get("data_admissao"), data.get("data_desligamento"))
    validar_status_colaborador(data.get("status", "pre_admissao"), data.get("data_desligamento"))
    validar_salario(data.get("salario_base"))


def criar(db: Session, data: dict, usuario_id: int | None = None):
    data = data.copy()
    _validar(data)
    return create_record(db, Colaborador, data, usuario_id)


def listar(db: Session):
    return list_records(db, Colaborador)


def buscar_por_id(db: Session, colaborador_id: int):
    return get_record(db, Colaborador, colaborador_id)


def editar(db: Session, colaborador_id: int, data: dict, usuario_id: int | None = None):
    data = data.copy()
    obj = buscar_por_id(db, colaborador_id)
    payload = {**obj.__dict__, **data}
    _validar(payload)
    return update_record(db, obj, data, usuario_id)


def remover(db: Session, colaborador_id: int, usuario_id: int | None = None):
    return soft_delete_record(db, buscar_por_id(db, colaborador_id), usuario_id)
