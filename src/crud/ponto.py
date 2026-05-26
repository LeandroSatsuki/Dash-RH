from __future__ import annotations

from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from src.crud import banco_horas as crud_banco_horas
from src.crud import jornadas as crud_jornadas
from src.db.models import (
    AjustePonto,
    Afastamento,
    ApuracaoPonto,
    Colaborador,
    Ferias,
    MarcacaoPonto,
    Turno,
)
from src.services.audit_service import log_action
from src.utils.money import safe_decimal

TIPOS_MARCACAO = {"entrada", "saida_intervalo", "retorno_intervalo", "saida", "ajuste_manual"}
ORIGENS_MARCACAO = {"manual", "importado_csv", "importado_excel", "sistema", "api"}
STATUS_AJUSTE = {"pendente", "aprovado", "reprovado", "cancelado"}


def _to_date(value) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _to_time(value) -> time:
    if isinstance(value, time):
        return value
    return time.fromisoformat(str(value))


def _to_decimal_hours(value) -> Decimal:
    decimal_value = safe_decimal(value)
    return decimal_value if decimal_value is not None else Decimal("0.00")


def _minutes_between(start: time, end: time, *, overnight: bool = False) -> int:
    base = date(2026, 1, 1)
    start_dt = datetime.combine(base, start)
    end_dt = datetime.combine(base, end)
    if overnight and end_dt < start_dt:
        end_dt += timedelta(days=1)
    return int((end_dt - start_dt).total_seconds() // 60)


def _expected_minutes(turno) -> int:
    if turno is None or turno.descanso:
        return 0
    if not turno.hora_entrada or not turno.hora_saida:
        return 0
    overnight = bool(turno.noturno)
    worked = _minutes_between(turno.hora_entrada, turno.hora_saida, overnight=overnight)
    if turno.hora_saida_intervalo and turno.hora_retorno_intervalo:
        worked -= _minutes_between(turno.hora_saida_intervalo, turno.hora_retorno_intervalo)
    return max(worked, 0)


def _actual_minutes(marcacoes: list[MarcacaoPonto], turno) -> tuple[int, int | None, int | None, bool]:
    if not marcacoes:
        return 0, None, None, True
    ordered = sorted(marcacoes, key=lambda item: item.horario)
    by_type = {item.tipo: item.horario for item in ordered}
    entrada = by_type.get("entrada")
    saida = by_type.get("saida")
    if entrada is None or saida is None:
        return 0, None, None, True
    overnight = bool(turno and turno.noturno)
    worked = _minutes_between(entrada, saida, overnight=overnight)
    if by_type.get("saida_intervalo") and by_type.get("retorno_intervalo"):
        worked -= _minutes_between(by_type["saida_intervalo"], by_type["retorno_intervalo"])
    atraso = None
    saida_antecipada = None
    if turno and turno.hora_entrada:
        atraso = max(_minutes_between(turno.hora_entrada, entrada), 0)
        tolerancia = turno_obj_tolerancia(turno, "entrada")
        if atraso <= tolerancia:
            atraso = 0
    if turno and turno.hora_saida:
        saida_antecipada = max(_minutes_between(saida, turno.hora_saida, overnight=overnight), 0)
        tolerancia = turno_obj_tolerancia(turno, "saida")
        if saida_antecipada <= tolerancia:
            saida_antecipada = 0
    inconsistent = len(ordered) not in {2, 4}
    return max(worked, 0), atraso, saida_antecipada, inconsistent


def turno_obj_tolerancia(turno, tipo: str) -> int:
    session = turno._sa_instance_state.session if turno is not None else None
    jornada = crud_jornadas.buscar_jornada(session, turno.jornada_id) if session is not None else None
    if jornada is None:
        return 0
    if tipo == "entrada":
        return int(jornada.tolerancia_entrada_minutos or 0)
    return int(jornada.tolerancia_saida_minutos or 0)


def _colaborador_disponivel_para_ponto(db: Session, colaborador: Colaborador, dia: date) -> tuple[bool, str]:
    if colaborador.deletado_em is not None:
        return False, "Colaborador removido."
    if colaborador.data_desligamento and dia > colaborador.data_desligamento:
        return False, "Colaborador desligado nao pode receber ponto apos a data de desligamento."
    if colaborador.status == "desligado":
        return False, "Colaborador desligado nao pode receber ponto."
    ferias = db.scalar(
        select(Ferias).where(
            Ferias.deletado_em.is_(None),
            Ferias.colaborador_id == colaborador.id,
            Ferias.data_inicio.is_not(None),
            Ferias.data_fim.is_not(None),
            Ferias.data_inicio <= dia,
            Ferias.data_fim >= dia,
            Ferias.status.in_(["aprovada", "em_gozo"]),
        )
    )
    if ferias is not None:
        return False, "Colaborador em ferias nao exige marcacao."
    afastamento = db.scalar(
        select(Afastamento).where(
            Afastamento.deletado_em.is_(None),
            Afastamento.colaborador_id == colaborador.id,
            Afastamento.status == "ativo",
            Afastamento.data_inicio <= dia,
            (Afastamento.data_fim.is_(None) | (Afastamento.data_fim >= dia)),
        )
    )
    if afastamento is not None:
        return False, "Colaborador afastado nao exige marcacao."
    return True, ""


def criar_marcacao(db: Session, data: dict, usuario_id: int | None = None) -> MarcacaoPonto:
    payload = data.copy()
    payload["data"] = _to_date(payload["data"])
    payload["horario"] = _to_time(payload["horario"])
    payload["tipo"] = str(payload["tipo"])
    payload["origem"] = str(payload.get("origem", "manual"))
    if payload["tipo"] not in TIPOS_MARCACAO:
        raise ValueError("Tipo de marcacao invalido.")
    if payload["origem"] not in ORIGENS_MARCACAO:
        raise ValueError("Origem de marcacao invalida.")
    colaborador = db.get(Colaborador, payload["colaborador_id"])
    if colaborador is None:
        raise ValueError("Colaborador nao encontrado.")
    permitido, motivo = _colaborador_disponivel_para_ponto(db, colaborador, payload["data"])
    if not permitido and colaborador.status == "desligado":
        raise ValueError(motivo)
    duplicada = db.scalar(
        select(MarcacaoPonto).where(
            MarcacaoPonto.deletado_em.is_(None),
            MarcacaoPonto.colaborador_id == payload["colaborador_id"],
            MarcacaoPonto.data == payload["data"],
            MarcacaoPonto.tipo == payload["tipo"],
            MarcacaoPonto.horario == payload["horario"],
        )
    )
    if duplicada is not None:
        raise ValueError("Marcacao duplicada para colaborador, data, tipo e horario.")
    payload["usuario_id"] = usuario_id
    obj = MarcacaoPonto(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    log_action(
        db,
        tabela="marcacoes_ponto",
        acao="marcacao_manual" if payload["origem"] == "manual" else "create",
        registro_id=obj.id,
        usuario_id=usuario_id,
        origem="ponto",
        valor_novo={"colaborador_id": obj.colaborador_id, "data": obj.data.isoformat(), "tipo": obj.tipo, "horario": obj.horario.isoformat()},
    )
    return obj


def listar_marcacoes(
    db: Session,
    *,
    colaborador_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> list[MarcacaoPonto]:
    stmt: Select = select(MarcacaoPonto).where(MarcacaoPonto.deletado_em.is_(None))
    if colaborador_id is not None:
        stmt = stmt.where(MarcacaoPonto.colaborador_id == colaborador_id)
    if data_inicio is not None:
        stmt = stmt.where(MarcacaoPonto.data >= data_inicio)
    if data_fim is not None:
        stmt = stmt.where(MarcacaoPonto.data <= data_fim)
    stmt = stmt.order_by(MarcacaoPonto.data.desc(), MarcacaoPonto.horario.asc())
    return list(db.scalars(stmt).all())


def listar_apuracoes(
    db: Session,
    *,
    colaborador_id: int | None = None,
    status: str | None = None,
) -> list[ApuracaoPonto]:
    stmt = select(ApuracaoPonto)
    if colaborador_id is not None:
        stmt = stmt.where(ApuracaoPonto.colaborador_id == colaborador_id)
    if status:
        stmt = stmt.where(ApuracaoPonto.status == status)
    stmt = stmt.order_by(ApuracaoPonto.data.desc())
    return list(db.scalars(stmt).all())


def apurar_periodo(
    db: Session,
    *,
    data_inicio: date,
    data_fim: date,
    usuario_id: int | None = None,
    colaborador_id: int | None = None,
    atualizar_banco_horas: bool = False,
) -> list[ApuracaoPonto]:
    if data_fim < data_inicio:
        raise ValueError("Periodo de apuracao invalido.")
    colaboradores_stmt = select(Colaborador).where(Colaborador.deletado_em.is_(None))
    if colaborador_id is not None:
        colaboradores_stmt = colaboradores_stmt.where(Colaborador.id == colaborador_id)
    colaboradores = list(db.scalars(colaboradores_stmt).all())
    resultados: list[ApuracaoPonto] = []
    dia = data_inicio
    while dia <= data_fim:
        for colaborador in colaboradores:
            jornada = crud_jornadas.jornada_atual_colaborador(db, colaborador.id, dia)
            turno = None
            if jornada is not None:
                turno = db.scalar(
                    select(Turno).where(
                        Turno.jornada_id == jornada.jornada_id,
                        Turno.dia_semana == dia.weekday(),
                        Turno.deletado_em.is_(None),
                    )
                )
            permitido, motivo = _colaborador_disponivel_para_ponto(db, colaborador, dia)
            horas_previstas = Decimal(str(_expected_minutes(turno) / 60)).quantize(Decimal("0.01")) if turno else Decimal("0.00")
            if not permitido and "desligado" in motivo.lower():
                continue
            marcacoes = listar_marcacoes(db, colaborador_id=colaborador.id, data_inicio=dia, data_fim=dia)
            horas_trabalhadas = Decimal("0.00")
            horas_extras = Decimal("0.00")
            horas_faltantes = Decimal("0.00")
            atraso = 0
            saida_antecipada = 0
            falta = False
            status = "apurado"
            if permitido:
                worked_minutes, atraso_val, saida_val, inconsistent = _actual_minutes(marcacoes, turno)
                horas_trabalhadas = Decimal(str(worked_minutes / 60)).quantize(Decimal("0.01"))
                atraso = int(atraso_val or 0)
                saida_antecipada = int(saida_val or 0)
                if horas_trabalhadas > horas_previstas:
                    horas_extras = (horas_trabalhadas - horas_previstas).quantize(Decimal("0.01"))
                else:
                    horas_faltantes = (horas_previstas - horas_trabalhadas).quantize(Decimal("0.01"))
                falta = horas_previstas > 0 and horas_trabalhadas == 0
                if inconsistent or (horas_previstas > 0 and len(marcacoes) == 0):
                    status = "inconsistente"
            else:
                status = "aprovado"
            existente = db.scalar(
                select(ApuracaoPonto).where(ApuracaoPonto.colaborador_id == colaborador.id, ApuracaoPonto.data == dia)
            )
            payload = {
                "colaborador_id": colaborador.id,
                "data": dia,
                "jornada_id": jornada.jornada_id if jornada else None,
                "horas_previstas": horas_previstas,
                "horas_trabalhadas": horas_trabalhadas,
                "horas_extras": horas_extras,
                "horas_faltantes": horas_faltantes,
                "atraso_minutos": atraso,
                "saida_antecipada_minutos": saida_antecipada,
                "adicional_noturno_horas": Decimal("0.00"),
                "falta": falta,
                "status": status,
            }
            if existente is None:
                apuracao = ApuracaoPonto(**payload)
                db.add(apuracao)
                db.commit()
                db.refresh(apuracao)
            else:
                for key, value in payload.items():
                    setattr(existente, key, value)
                db.add(existente)
                db.commit()
                db.refresh(existente)
                apuracao = existente
            if atualizar_banco_horas and permitido:
                if horas_extras > 0:
                    crud_banco_horas.criar_movimento(
                        db,
                        {
                            "colaborador_id": colaborador.id,
                            "data": dia,
                            "origem": "apuracao_ponto",
                            "tipo": "credito",
                            "horas": horas_extras,
                            "descricao": f"Credito por apuracao de ponto em {dia.isoformat()}",
                        },
                        usuario_id,
                    )
                if horas_faltantes > 0:
                    crud_banco_horas.criar_movimento(
                        db,
                        {
                            "colaborador_id": colaborador.id,
                            "data": dia,
                            "origem": "apuracao_ponto",
                            "tipo": "debito",
                            "horas": horas_faltantes,
                            "descricao": f"Debito por apuracao de ponto em {dia.isoformat()}",
                        },
                        usuario_id,
                    )
            resultados.append(apuracao)
        dia += timedelta(days=1)
    log_action(
        db,
        tabela="apuracoes_ponto",
        acao="apurar_periodo",
        usuario_id=usuario_id,
        origem="ponto",
        valor_novo={"data_inicio": data_inicio.isoformat(), "data_fim": data_fim.isoformat(), "colaborador_id": colaborador_id},
    )
    return resultados


def criar_ajuste(db: Session, data: dict, usuario_id: int | None = None) -> AjustePonto:
    payload = data.copy()
    payload["data"] = _to_date(payload["data"])
    if not payload.get("motivo"):
        raise ValueError("Ajuste de ponto exige motivo.")
    ajuste = AjustePonto(
        colaborador_id=payload["colaborador_id"],
        data=payload["data"],
        tipo_ajuste=payload["tipo_ajuste"],
        motivo=payload["motivo"],
        valor_anterior=payload.get("valor_anterior"),
        valor_novo=payload.get("valor_novo"),
        status="pendente",
        solicitante_id=usuario_id,
    )
    db.add(ajuste)
    db.commit()
    db.refresh(ajuste)
    log_action(db, tabela="ajustes_ponto", acao="create", registro_id=ajuste.id, usuario_id=usuario_id, origem="ponto", valor_novo=payload)
    return ajuste


def aprovar_ajuste(db: Session, ajuste_id: int, usuario_id: int | None = None) -> AjustePonto:
    ajuste = db.get(AjustePonto, ajuste_id)
    if ajuste is None:
        raise ValueError("Ajuste nao encontrado.")
    ajuste.status = "aprovado"
    ajuste.aprovador_id = usuario_id
    db.add(ajuste)
    db.commit()
    db.refresh(ajuste)
    log_action(db, tabela="ajustes_ponto", acao="aprovar_ajuste", registro_id=ajuste.id, usuario_id=usuario_id, origem="ponto")
    return ajuste


def reprovar_ajuste(db: Session, ajuste_id: int, usuario_id: int | None = None) -> AjustePonto:
    ajuste = db.get(AjustePonto, ajuste_id)
    if ajuste is None:
        raise ValueError("Ajuste nao encontrado.")
    ajuste.status = "reprovado"
    ajuste.aprovador_id = usuario_id
    db.add(ajuste)
    db.commit()
    db.refresh(ajuste)
    log_action(db, tabela="ajustes_ponto", acao="reprovar_ajuste", registro_id=ajuste.id, usuario_id=usuario_id, origem="ponto")
    return ajuste


def listar_ajustes(db: Session, *, status: str | None = None) -> list[AjustePonto]:
    stmt = select(AjustePonto)
    if status and status in STATUS_AJUSTE:
        stmt = stmt.where(AjustePonto.status == status)
    stmt = stmt.order_by(AjustePonto.criado_em.desc())
    return list(db.scalars(stmt).all())


def resumo_por_colaborador(db: Session, colaborador_id: int) -> dict:
    stmt = (
        select(
            func.coalesce(func.sum(ApuracaoPonto.horas_previstas), 0),
            func.coalesce(func.sum(ApuracaoPonto.horas_trabalhadas), 0),
            func.coalesce(func.sum(ApuracaoPonto.horas_extras), 0),
            func.coalesce(func.sum(ApuracaoPonto.horas_faltantes), 0),
        )
        .where(ApuracaoPonto.colaborador_id == colaborador_id)
    )
    previstas, trabalhadas, extras, faltantes = db.execute(stmt).one()
    return {
        "colaborador_id": colaborador_id,
        "horas_previstas": float(previstas or 0),
        "horas_trabalhadas": float(trabalhadas or 0),
        "horas_extras": float(extras or 0),
        "horas_faltantes": float(faltantes or 0),
        "saldo_banco_horas": float(crud_banco_horas.saldo_colaborador(db, colaborador_id)),
    }


def resumo_por_departamento(db: Session) -> list[dict]:
    rows = db.execute(
        select(
            Colaborador.departamento_id,
            func.coalesce(func.sum(ApuracaoPonto.horas_previstas), 0),
            func.coalesce(func.sum(ApuracaoPonto.horas_trabalhadas), 0),
            func.coalesce(func.sum(ApuracaoPonto.horas_extras), 0),
            func.coalesce(func.sum(ApuracaoPonto.horas_faltantes), 0),
        )
        .join(Colaborador, Colaborador.id == ApuracaoPonto.colaborador_id)
        .group_by(Colaborador.departamento_id)
    ).all()
    return [
        {
            "departamento_id": departamento_id,
            "horas_previstas": float(previstas or 0),
            "horas_trabalhadas": float(trabalhadas or 0),
            "horas_extras": float(extras or 0),
            "horas_faltantes": float(faltantes or 0),
        }
        for departamento_id, previstas, trabalhadas, extras, faltantes in rows
    ]
