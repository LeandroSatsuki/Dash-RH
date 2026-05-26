from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from src.schemas.common import ORMModel


class CompetenciaFolhaBase(BaseModel):
    ano: int
    mes: int
    competencia: str
    status: str = "aberta"
    observacao: str | None = None


class CompetenciaFolhaCreate(CompetenciaFolhaBase):
    pass


class CompetenciaFolhaUpdate(BaseModel):
    status: str | None = None
    observacao: str | None = None


class CompetenciaFolhaOut(ORMModel, CompetenciaFolhaBase):
    id: int
    data_abertura: datetime | None = None
    data_fechamento: datetime | None = None
    usuario_fechamento_id: int | None = None
    criado_em: datetime
    atualizado_em: datetime


class RubricaBase(BaseModel):
    codigo: str
    descricao: str
    tipo: str
    natureza: str | None = None
    incide_inss: bool = False
    incide_fgts: bool = False
    incide_irrf: bool = False
    ativo: bool = True


class RubricaCreate(RubricaBase):
    pass


class RubricaUpdate(BaseModel):
    descricao: str | None = None
    tipo: str | None = None
    natureza: str | None = None
    incide_inss: bool | None = None
    incide_fgts: bool | None = None
    incide_irrf: bool | None = None
    ativo: bool | None = None


class RubricaOut(ORMModel, RubricaBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime


class LancamentoFolhaBase(BaseModel):
    competencia_id: int
    colaborador_id: int
    rubrica_id: int
    tipo: str
    valor: Decimal
    quantidade: float | None = None
    origem: str = "manual"
    observacao: str | None = None


class LancamentoFolhaCreate(LancamentoFolhaBase):
    pass


class LancamentoFolhaUpdate(BaseModel):
    tipo: str | None = None
    valor: Decimal | None = None
    quantidade: float | None = None
    origem: str | None = None
    observacao: str | None = None


class LancamentoFolhaOut(ORMModel, LancamentoFolhaBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
