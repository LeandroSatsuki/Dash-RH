from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, update_record
from src.db.models import Beneficio, Colaborador, ColaboradorBeneficio
from src.services.audit_service import log_action
from src.utils.money import safe_decimal


def criar(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, Beneficio, data, usuario_id)


def listar(db: Session):
    return list_records(db, Beneficio, include_deleted=True)


def buscar_por_id(db: Session, beneficio_id: int):
    return get_record(db, Beneficio, beneficio_id)


def editar(db: Session, beneficio_id: int, data: dict, usuario_id: int | None = None):
    return update_record(db, buscar_por_id(db, beneficio_id), data, usuario_id)


def remover(db: Session, beneficio_id: int, usuario_id: int | None = None):
    obj = buscar_por_id(db, beneficio_id)
    obj.status = "inativo"
    return update_record(db, obj, {"status": "inativo"}, usuario_id)


def _validar_vinculo(data: dict, colaborador: Colaborador | None = None) -> None:
    valor_empresa = safe_decimal(data.get("valor_empresa"))
    valor_colaborador = safe_decimal(data.get("valor_colaborador"))
    if valor_empresa is not None and valor_empresa < 0:
        raise ValueError("Valor empresa nao pode ser negativo.")
    if valor_colaborador is not None and valor_colaborador < 0:
        raise ValueError("Valor colaborador nao pode ser negativo.")
    if data.get("status", "ativo") == "ativo" and not data.get("data_inicio"):
        raise ValueError("Beneficio ativo deve ter data inicio.")
    if data.get("status") == "encerrado" and not data.get("data_fim"):
        raise ValueError("Beneficio encerrado deve ter data fim.")
    if colaborador is not None and colaborador.status == "desligado" and data.get("status", "ativo") == "ativo":
        raise ValueError("Colaborador desligado nao deve receber novo beneficio ativo.")


def vincular_ao_colaborador(db: Session, data: dict, usuario_id: int | None = None):
    colaborador = db.get(Colaborador, data["colaborador_id"])
    _validar_vinculo(data, colaborador)
    payload = data.copy()
    payload["valor_empresa"] = safe_decimal(payload.get("valor_empresa"))
    payload["valor_colaborador"] = safe_decimal(payload.get("valor_colaborador"))
    return create_record(db, ColaboradorBeneficio, payload, usuario_id)


def listar_vinculos(db: Session):
    return list_records(db, ColaboradorBeneficio, include_deleted=True)


def buscar_vinculo_por_id(db: Session, vinculo_id: int):
    return get_record(db, ColaboradorBeneficio, vinculo_id)


def editar_vinculo(db: Session, vinculo_id: int, data: dict, usuario_id: int | None = None):
    vinculo = buscar_vinculo_por_id(db, vinculo_id)
    payload = {**vinculo.__dict__, **data}
    payload["valor_empresa"] = safe_decimal(payload.get("valor_empresa"))
    payload["valor_colaborador"] = safe_decimal(payload.get("valor_colaborador"))
    colaborador = db.get(Colaborador, vinculo.colaborador_id)
    _validar_vinculo(payload, colaborador)
    return update_record(db, vinculo, {**data, "valor_empresa": payload.get("valor_empresa"), "valor_colaborador": payload.get("valor_colaborador")}, usuario_id)


def encerrar_vinculo(db: Session, vinculo_id: int, usuario_id: int | None = None, data_fim: date | None = None):
    vinculo = buscar_vinculo_por_id(db, vinculo_id)
    updated = update_record(db, vinculo, {"status": "encerrado", "data_fim": data_fim or date.today()}, usuario_id)
    log_action(db, tabela="colaborador_beneficios", acao="encerrar_beneficio", registro_id=updated.id, usuario_id=usuario_id, origem="beneficios")
    return updated


def colaboradores_sem_beneficio(db: Session, nomes_beneficios: set[str]) -> list[Colaborador]:
    vinculos = db.scalars(select(ColaboradorBeneficio)).all()
    beneficios = {item.id: item for item in listar(db)}
    ativos_por_colaborador = {}
    for vinculo in vinculos:
        if vinculo.status != "ativo":
            continue
        ativos_por_colaborador.setdefault(vinculo.colaborador_id, set()).add((beneficios.get(vinculo.beneficio_id).nome if beneficios.get(vinculo.beneficio_id) else ""))
    resultado = []
    for colaborador in list_records(db, Colaborador):
        if colaborador.status == "desligado":
            continue
        if not nomes_beneficios.intersection(ativos_por_colaborador.get(colaborador.id, set())):
            resultado.append(colaborador)
    return resultado
