from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud.base import create_record, list_records, update_record
from src.db.models import BancoHorasMovimento, ConfiguracaoSistema
from src.services.audit_service import log_action
from src.utils.money import safe_decimal


def _get_config(db: Session, chave: str, default: str) -> str:
    item = db.scalar(select(ConfiguracaoSistema).where(ConfiguracaoSistema.chave == chave))
    return item.valor if item else default


def set_config(db: Session, chave: str, valor: str, descricao: str | None = None, usuario_id: int | None = None):
    item = db.scalar(select(ConfiguracaoSistema).where(ConfiguracaoSistema.chave == chave))
    if item is None:
        return create_record(db, ConfiguracaoSistema, {"chave": chave, "valor": valor, "descricao": descricao}, usuario_id)
    return update_record(db, item, {"valor": valor, "descricao": descricao}, usuario_id)


def criar_movimento(db: Session, data: dict, usuario_id: int | None = None):
    payload = data.copy()
    payload["horas"] = safe_decimal(payload.get("horas")) or Decimal("0")
    if payload["tipo"] == "ajuste" and not payload.get("descricao"):
        raise ValueError("Ajuste de banco de horas exige motivo.")
    if payload["tipo"] == "debito":
        saldo = saldo_colaborador(db, payload["colaborador_id"])
        permitir_negativo = _get_config(db, "permitir_banco_horas_negativo", "true").lower() == "true"
        limite_negativo = safe_decimal(_get_config(db, "limite_horas_negativas", "-40")) or Decimal("-40")
        novo_saldo = saldo - payload["horas"]
        if not permitir_negativo and novo_saldo < 0:
            raise ValueError("Saldo negativo de banco de horas bloqueado pela configuracao.")
        if novo_saldo < limite_negativo:
            raise ValueError("Saldo de banco de horas abaixo do limite permitido.")
    movimento = create_record(db, BancoHorasMovimento, payload, usuario_id)
    if payload["origem"] == "ajuste_manual":
        log_action(db, tabela="banco_horas_movimentos", acao="ajuste_banco_horas", registro_id=movimento.id, usuario_id=usuario_id, origem="banco_horas")
    return movimento


def listar_movimentos(db: Session):
    return list_records(db, BancoHorasMovimento, include_deleted=True)


def saldo_colaborador(db: Session, colaborador_id: int) -> Decimal:
    saldo = Decimal("0")
    for item in db.scalars(select(BancoHorasMovimento).where(BancoHorasMovimento.colaborador_id == colaborador_id)).all():
        horas = safe_decimal(item.horas) or Decimal("0")
        if item.tipo == "credito":
            saldo += horas
        elif item.tipo == "debito":
            saldo -= horas
        else:
            saldo += horas
    return saldo


def saldo_por_departamento(db: Session) -> list[dict]:
    from src.db.models import Colaborador

    acumulado: dict[int | None, Decimal] = {}
    colaboradores = {item.id: item for item in db.scalars(select(Colaborador)).all()}
    for item in listar_movimentos(db):
        depto = colaboradores.get(item.colaborador_id).departamento_id if colaboradores.get(item.colaborador_id) else None
        acumulado.setdefault(depto, Decimal("0"))
        horas = safe_decimal(item.horas) or Decimal("0")
        if item.tipo == "debito":
            acumulado[depto] -= horas
        else:
            acumulado[depto] += horas
    return [{"departamento_id": key, "saldo": float(value)} for key, value in acumulado.items()]
