from __future__ import annotations

from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, soft_delete_record, update_record
from src.db.models import Colaborador, ColaboradorJornada, Jornada, Turno
from src.services.audit_service import log_action
from src.services.historico import registrar_historico
from src.utils.money import safe_decimal


def _to_time(value):
    if value in (None, ""):
        return None
    if isinstance(value, time):
        return value
    if isinstance(value, datetime):
        return value.time()
    return time.fromisoformat(str(value))


def _validar_turno(data: dict) -> None:
    if data.get("descanso"):
        return
    entrada = _to_time(data.get("hora_entrada"))
    saida = _to_time(data.get("hora_saida"))
    noturno = bool(data.get("noturno"))
    if entrada is None or saida is None:
        raise ValueError("Turno sem descanso exige hora de entrada e saida.")
    if saida < entrada and not noturno:
        raise ValueError("Hora de saida nao pode ser menor que entrada sem marcacao noturna.")


def criar_jornada(db: Session, data: dict, usuario_id: int | None = None):
    payload = data.copy()
    payload["carga_horaria_semanal"] = safe_decimal(payload.get("carga_horaria_semanal"))
    payload["carga_horaria_diaria"] = safe_decimal(payload.get("carga_horaria_diaria"))
    return create_record(db, Jornada, payload, usuario_id)


def listar_jornadas(db: Session):
    return list_records(db, Jornada)


def buscar_jornada(db: Session, jornada_id: int):
    return get_record(db, Jornada, jornada_id)


def editar_jornada(db: Session, jornada_id: int, data: dict, usuario_id: int | None = None):
    payload = data.copy()
    if "carga_horaria_semanal" in payload:
        payload["carga_horaria_semanal"] = safe_decimal(payload.get("carga_horaria_semanal"))
    if "carga_horaria_diaria" in payload:
        payload["carga_horaria_diaria"] = safe_decimal(payload.get("carga_horaria_diaria"))
    return update_record(db, buscar_jornada(db, jornada_id), payload, usuario_id)


def remover_jornada(db: Session, jornada_id: int, usuario_id: int | None = None):
    return soft_delete_record(db, buscar_jornada(db, jornada_id), usuario_id)


def criar_turno(db: Session, jornada_id: int, data: dict, usuario_id: int | None = None):
    payload = {"jornada_id": jornada_id, **data}
    payload["hora_entrada"] = _to_time(payload.get("hora_entrada"))
    payload["hora_saida_intervalo"] = _to_time(payload.get("hora_saida_intervalo"))
    payload["hora_retorno_intervalo"] = _to_time(payload.get("hora_retorno_intervalo"))
    payload["hora_saida"] = _to_time(payload.get("hora_saida"))
    _validar_turno(payload)
    return create_record(db, Turno, payload, usuario_id)


def listar_turnos_jornada(db: Session, jornada_id: int):
    stmt = select(Turno).where(Turno.jornada_id == jornada_id, Turno.deletado_em.is_(None)).order_by(Turno.dia_semana.asc())
    return list(db.scalars(stmt).all())


def vincular_jornada_colaborador(db: Session, colaborador_id: int, data: dict, usuario_id: int | None = None):
    data_inicio = data["data_inicio"]
    data_fim = data.get("data_fim")
    ativos = db.scalars(
        select(ColaboradorJornada).where(
            ColaboradorJornada.colaborador_id == colaborador_id,
            ColaboradorJornada.ativo.is_(True),
        )
    ).all()
    for item in ativos:
        item.ativo = False
        if item.data_fim is None or item.data_fim >= data_inicio:
            item.data_fim = data_inicio
        db.add(item)
    db.commit()
    vinculo = create_record(db, ColaboradorJornada, {"colaborador_id": colaborador_id, **data, "ativo": True}, usuario_id)
    registrar_historico(
        db,
        colaborador_id=colaborador_id,
        tipo_evento="alteracao_jornada",
        data_evento=data_inicio,
        data_inicio=data_inicio,
        data_fim=data_fim,
        usuario_id=usuario_id,
        campo_alterado="jornada",
        valor_novo=str(vinculo.jornada_id),
        motivo="Vinculo de jornada",
    )
    log_action(db, tabela="colaborador_jornadas", acao="vincular_jornada", registro_id=vinculo.id, usuario_id=usuario_id, origem="jornadas")
    return vinculo


def jornada_atual_colaborador(db: Session, colaborador_id: int, referencia: date | None = None):
    referencia = referencia or date.today()
    stmt = select(ColaboradorJornada).where(
        ColaboradorJornada.colaborador_id == colaborador_id,
        ColaboradorJornada.data_inicio <= referencia,
        (ColaboradorJornada.data_fim.is_(None) | (ColaboradorJornada.data_fim >= referencia)),
        ColaboradorJornada.ativo.is_(True),
    )
    return db.scalar(stmt)
