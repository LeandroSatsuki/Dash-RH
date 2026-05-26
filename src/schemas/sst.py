from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class ExameOcupacionalCreate(BaseModel):
    colaborador_id: int
    tipo_exame: str
    data_exame: date
    data_validade: date | None = None
    clinica: str | None = None
    resultado: str | None = None
    documento_id: int | None = None
    status: str = "ativo"
    observacao: str | None = None


class ExameOcupacionalOut(ORMModel, ExameOcupacionalCreate):
    id: int
    criado_em: datetime
    atualizado_em: datetime


class EPICreate(BaseModel):
    nome: str
    ca: str | None = None
    validade_ca: date | None = None
    ativo: bool = True


class EPIOut(ORMModel, EPICreate):
    id: int
    criado_em: datetime
    atualizado_em: datetime


class EntregaEPICreate(BaseModel):
    colaborador_id: int
    epi_id: int
    data_entrega: date
    data_devolucao: date | None = None
    quantidade: int = 1
    termo_documento_id: int | None = None
    status: str = "ativo"


class EntregaEPIOut(ORMModel, EntregaEPICreate):
    id: int
    criado_em: datetime
    atualizado_em: datetime


class TreinamentoSSTCreate(BaseModel):
    nome: str
    descricao: str | None = None
    validade_meses: int | None = None
    ativo: bool = True


class TreinamentoSSTOut(ORMModel, TreinamentoSSTCreate):
    id: int
    criado_em: datetime
    atualizado_em: datetime


class ColaboradorTreinamentoSSTCreate(BaseModel):
    colaborador_id: int
    treinamento_id: int
    data_realizacao: date
    data_validade: date | None = None
    documento_id: int | None = None
    status: str = "ativo"


class ColaboradorTreinamentoSSTOut(ORMModel, ColaboradorTreinamentoSSTCreate):
    id: int
    criado_em: datetime
    atualizado_em: datetime
