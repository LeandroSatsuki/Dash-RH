from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class CargoBase(BaseModel):
    nome: str
    cbo: str | None = None
    departamento_id: int | None = None
    descricao: str | None = None
    status: str = "ativo"


class CargoCreate(CargoBase):
    pass


class CargoUpdate(BaseModel):
    nome: str | None = None
    cbo: str | None = None
    departamento_id: int | None = None
    descricao: str | None = None
    status: str | None = None


class CargoOut(ORMModel, CargoBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
