from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from src.schemas.common import ORMModel


class BeneficioBase(BaseModel):
    nome: str
    tipo: str | None = None
    operadora: str | None = None
    status: str = "ativo"


class BeneficioCreate(BeneficioBase):
    pass


class BeneficioUpdate(BaseModel):
    nome: str | None = None
    tipo: str | None = None
    operadora: str | None = None
    status: str | None = None


class BeneficioOut(ORMModel, BeneficioBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime


class ColaboradorBeneficioBase(BaseModel):
    colaborador_id: int
    beneficio_id: int
    data_inicio: date | None = None
    data_fim: date | None = None
    valor_empresa: Decimal | None = None
    valor_colaborador: Decimal | None = None
    dependentes: int | None = None
    status: str = "ativo"
    observacao: str | None = None


class ColaboradorBeneficioCreate(ColaboradorBeneficioBase):
    pass


class ColaboradorBeneficioOut(ORMModel, ColaboradorBeneficioBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
