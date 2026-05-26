from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel

from src.schemas.common import ORMModel


class MarcacaoPontoCreate(BaseModel):
    colaborador_id: int
    data: date
    tipo: str
    horario: time
    origem: str = "manual"
    observacao: str | None = None


class MarcacaoPontoOut(ORMModel, MarcacaoPontoCreate):
    id: int
    usuario_id: int | None = None
    criado_em: datetime
    atualizado_em: datetime
    deletado_em: datetime | None = None


class ApuracaoPontoRequest(BaseModel):
    data_inicio: date
    data_fim: date
    colaborador_id: int | None = None
    atualizar_banco_horas: bool = False


class ApuracaoPontoOut(ORMModel):
    id: int
    colaborador_id: int
    data: date
    jornada_id: int | None = None
    horas_previstas: Decimal | None = None
    horas_trabalhadas: Decimal | None = None
    horas_extras: Decimal | None = None
    horas_faltantes: Decimal | None = None
    atraso_minutos: int | None = None
    saida_antecipada_minutos: int | None = None
    adicional_noturno_horas: Decimal | None = None
    falta: bool
    status: str
    criado_em: datetime
    atualizado_em: datetime


class AjustePontoCreate(BaseModel):
    colaborador_id: int
    data: date
    tipo_ajuste: str
    motivo: str
    valor_anterior: str | None = None
    valor_novo: str | None = None


class AjustePontoOut(ORMModel, AjustePontoCreate):
    id: int
    status: str
    solicitante_id: int | None = None
    aprovador_id: int | None = None
    criado_em: datetime
    atualizado_em: datetime
