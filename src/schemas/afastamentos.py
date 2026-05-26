from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class AfastamentoBase(BaseModel):
    colaborador_id: int
    tipo: str
    data_inicio: date
    data_fim: date | None = None
    quantidade_dias: float | None = None
    quantidade_horas: float | None = None
    impacta_folha: bool = False
    impacta_absenteismo: bool = True
    cid_mascarado: str | None = None
    status: str = "ativo"
    observacao: str | None = None


class AfastamentoCreate(AfastamentoBase):
    pass


class AfastamentoUpdate(BaseModel):
    tipo: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    quantidade_dias: float | None = None
    quantidade_horas: float | None = None
    impacta_folha: bool | None = None
    impacta_absenteismo: bool | None = None
    cid_mascarado: str | None = None
    status: str | None = None
    observacao: str | None = None


class AfastamentoOut(ORMModel, AfastamentoBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
