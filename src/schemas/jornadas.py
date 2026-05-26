from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel

from src.schemas.common import ORMModel


class JornadaBase(BaseModel):
    nome: str
    descricao: str | None = None
    carga_horaria_semanal: Decimal | None = None
    carga_horaria_diaria: Decimal | None = None
    tolerancia_entrada_minutos: int | None = None
    tolerancia_saida_minutos: int | None = None
    intervalo_minimo_minutos: int | None = None
    ativo: bool = True


class JornadaCreate(JornadaBase):
    pass


class JornadaUpdate(BaseModel):
    descricao: str | None = None
    carga_horaria_semanal: Decimal | None = None
    carga_horaria_diaria: Decimal | None = None
    tolerancia_entrada_minutos: int | None = None
    tolerancia_saida_minutos: int | None = None
    intervalo_minimo_minutos: int | None = None
    ativo: bool | None = None


class JornadaOut(ORMModel, JornadaBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
    deletado_em: datetime | None = None


class TurnoCreate(BaseModel):
    dia_semana: int
    hora_entrada: time | None = None
    hora_saida_intervalo: time | None = None
    hora_retorno_intervalo: time | None = None
    hora_saida: time | None = None
    descanso: bool = False
    noturno: bool = False


class TurnoOut(ORMModel, TurnoCreate):
    id: int
    jornada_id: int
    criado_em: datetime
    atualizado_em: datetime
    deletado_em: datetime | None = None


class ColaboradorJornadaCreate(BaseModel):
    jornada_id: int
    data_inicio: date
    data_fim: date | None = None
    ativo: bool = True
    observacao: str | None = None


class ColaboradorJornadaOut(ORMModel, ColaboradorJornadaCreate):
    id: int
    colaborador_id: int
    criado_em: datetime
    atualizado_em: datetime
