from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from src.schemas.common import ORMModel


class ColaboradorBase(BaseModel):
    matricula: str | None = None
    nome_completo: str
    nome_social: str | None = None
    cpf: str | None = None
    rg: str | None = None
    data_nascimento: date | None = None
    email: str | None = None
    telefone: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    uf: str | None = None
    regime_contratual: str | None = None
    tipo_vinculo: str | None = None
    data_admissao: date | None = None
    data_desligamento: date | None = None
    cargo_id: int | None = None
    departamento_id: int | None = None
    centro_custo_id: int | None = None
    salario_base: Decimal | None = None
    jornada_semanal: float | None = None
    gestor_id: int | None = None
    status: str = "pre_admissao"
    origem: str = "manual"


class ColaboradorCreate(ColaboradorBase):
    pass


class ColaboradorUpdate(BaseModel):
    matricula: str | None = None
    nome_completo: str | None = None
    nome_social: str | None = None
    cpf: str | None = None
    rg: str | None = None
    data_nascimento: date | None = None
    email: str | None = None
    telefone: str | None = None
    endereco: str | None = None
    cidade: str | None = None
    uf: str | None = None
    regime_contratual: str | None = None
    tipo_vinculo: str | None = None
    data_admissao: date | None = None
    data_desligamento: date | None = None
    cargo_id: int | None = None
    departamento_id: int | None = None
    centro_custo_id: int | None = None
    salario_base: Decimal | None = None
    jornada_semanal: float | None = None
    gestor_id: int | None = None
    status: str | None = None
    origem: str | None = None


class ColaboradorOut(ORMModel, ColaboradorBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
