from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, soft_delete_record, update_record
from src.db.models import Colaborador, Ferias
from src.services.audit_service import log_action
from src.services.historico import registrar_historico
from src.services.validacoes_dp import validar_periodo


def _validar(data: dict) -> None:
    validar_periodo(data.get("data_inicio"), data.get("data_fim"), "Férias")
    dias_direito = float(data.get("dias_direito") or 0)
    dias_gozados = float(data.get("dias_gozados") or 0)
    if dias_gozados > dias_direito:
        raise ValueError("Dias gozados nao pode ser maior que dias de direito.")


def _validar_sobreposicao(db: Session, colaborador_id: int, data_inicio: date | None, data_fim: date | None, ferias_id: int | None = None) -> None:
    if not data_inicio or not data_fim:
        return
    for item in listar(db):
        if item.colaborador_id != colaborador_id or item.id == ferias_id or item.status == "cancelada":
            continue
        if item.data_inicio and item.data_fim and not (data_fim < item.data_inicio or data_inicio > item.data_fim):
            raise ValueError("Nao e possivel aprovar ferias sobrepostas para o mesmo colaborador.")


def criar(db: Session, data: dict, usuario_id: int | None = None):
    _validar(data)
    return create_record(db, Ferias, data, usuario_id)


def listar(db: Session):
    return list_records(db, Ferias)


def buscar_por_id(db: Session, ferias_id: int):
    return get_record(db, Ferias, ferias_id)


def editar(db: Session, ferias_id: int, data: dict, usuario_id: int | None = None):
    obj = buscar_por_id(db, ferias_id)
    payload = {**obj.__dict__, **data}
    _validar(payload)
    return update_record(db, obj, data, usuario_id)


def aprovar(db: Session, ferias_id: int, usuario_id: int | None = None):
    obj = buscar_por_id(db, ferias_id)
    colaborador = db.get(Colaborador, obj.colaborador_id)
    if colaborador is None:
        raise ValueError("Colaborador nao encontrado.")
    if colaborador.status == "desligado":
        raise ValueError("Nao e possivel aprovar ferias para colaborador desligado.")
    _validar_sobreposicao(db, obj.colaborador_id, obj.data_inicio, obj.data_fim, obj.id)
    updated = update_record(db, obj, {"status": "aprovada"}, usuario_id)
    log_action(db, tabela="ferias", acao="aprovar_ferias", registro_id=obj.id, usuario_id=usuario_id, origem="ferias")
    return updated


def cancelar(db: Session, ferias_id: int, usuario_id: int | None = None, motivo: str | None = None):
    obj = buscar_por_id(db, ferias_id)
    updated = update_record(db, obj, {"status": "cancelada", "observacao": motivo or obj.observacao}, usuario_id)
    log_action(db, tabela="ferias", acao="cancelar_ferias", registro_id=obj.id, usuario_id=usuario_id, origem="ferias")
    return updated


def concluir(db: Session, ferias_id: int, usuario_id: int | None = None):
    obj = buscar_por_id(db, ferias_id)
    colaborador = db.get(Colaborador, obj.colaborador_id)
    updated = update_record(db, obj, {"status": "concluida"}, usuario_id)
    if colaborador is not None:
        registrar_historico(
            db,
            colaborador_id=colaborador.id,
            tipo_evento="ferias",
            data_evento=obj.data_inicio or date.today(),
            data_inicio=obj.data_inicio,
            data_fim=obj.data_fim,
            usuario_id=usuario_id,
            motivo="Conclusao de ferias",
        )
        registrar_historico(
            db,
            colaborador_id=colaborador.id,
            tipo_evento="retorno_ferias",
            data_evento=obj.data_fim or date.today(),
            data_inicio=obj.data_inicio,
            data_fim=obj.data_fim,
            usuario_id=usuario_id,
            motivo="Retorno de ferias",
        )
    log_action(db, tabela="ferias", acao="concluir_ferias", registro_id=obj.id, usuario_id=usuario_id, origem="ferias")
    return updated


def alertas_a_vencer(db: Session, dias: int) -> list[Ferias]:
    limite = date.today() + timedelta(days=dias)
    stmt = select(Ferias).where(
        Ferias.deletado_em.is_(None),
        Ferias.data_limite_gozo.is_not(None),
        Ferias.data_limite_gozo <= limite,
        Ferias.status != "concluida",
    )
    return list(db.scalars(stmt).all())


def remover(db: Session, ferias_id: int, usuario_id: int | None = None):
    return soft_delete_record(db, buscar_por_id(db, ferias_id), usuario_id)
