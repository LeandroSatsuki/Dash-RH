from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from src.schemas.common import ORMModel


class BancoHorasMovimentoCreate(BaseModel):
    colaborador_id: int
    data: date
    origem: str
    tipo: str
    horas: Decimal
    descricao: str | None = None
    competencia_id: int | None = None


class BancoHorasMovimentoOut(ORMModel, BancoHorasMovimentoCreate):
    id: int
    criado_em: datetime
    atualizado_em: datetime
