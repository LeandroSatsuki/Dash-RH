from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class CentroCustoBase(BaseModel):
    codigo: str
    nome: str
    area: str | None = None
    subarea: str | None = None
    status: str = "ativo"


class CentroCustoCreate(CentroCustoBase):
    pass


class CentroCustoUpdate(BaseModel):
    codigo: str | None = None
    nome: str | None = None
    area: str | None = None
    subarea: str | None = None
    status: str | None = None


class CentroCustoOut(ORMModel, CentroCustoBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
