from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class DepartamentoBase(BaseModel):
    nome: str
    descricao: str | None = None
    gestor_id: int | None = None
    status: str = "ativo"


class DepartamentoCreate(DepartamentoBase):
    pass


class DepartamentoUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    gestor_id: int | None = None
    status: str | None = None


class DepartamentoOut(ORMModel, DepartamentoBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
