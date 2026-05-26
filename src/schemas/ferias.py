from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class FeriasBase(BaseModel):
    colaborador_id: int
    periodo_aquisitivo_inicio: date | None = None
    periodo_aquisitivo_fim: date | None = None
    data_limite_gozo: date | None = None
    dias_direito: float | None = None
    dias_gozados: float | None = None
    dias_restantes: float | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    abono_pecuniario: bool = False
    adiantamento_13: bool = False
    status: str = "planejada"
    observacao: str | None = None


class FeriasCreate(FeriasBase):
    pass


class FeriasUpdate(BaseModel):
    periodo_aquisitivo_inicio: date | None = None
    periodo_aquisitivo_fim: date | None = None
    data_limite_gozo: date | None = None
    dias_direito: float | None = None
    dias_gozados: float | None = None
    dias_restantes: float | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    abono_pecuniario: bool | None = None
    adiantamento_13: bool | None = None
    status: str | None = None
    observacao: str | None = None


class FeriasOut(ORMModel, FeriasBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
