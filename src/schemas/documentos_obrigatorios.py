from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class TipoDocumentoCreate(BaseModel):
    nome: str
    descricao: str | None = None
    sensivel: bool = False
    exige_validade: bool = False
    ativo: bool = True


class TipoDocumentoOut(ORMModel, TipoDocumentoCreate):
    id: int
    criado_em: datetime
    atualizado_em: datetime


class DocumentoObrigatorioRegraCreate(BaseModel):
    tipo_documento_id: int
    regime_contratual: str | None = None
    cargo_id: int | None = None
    departamento_id: int | None = None
    obrigatorio: bool = True
    validade_dias: int | None = None


class DocumentoObrigatorioRegraOut(ORMModel, DocumentoObrigatorioRegraCreate):
    id: int
    criado_em: datetime
    atualizado_em: datetime


class DocumentoPendenciaOut(ORMModel):
    id: int
    colaborador_id: int
    tipo_documento_id: int
    status: str
    data_vencimento: date | None = None
    severidade: str
    resolvido_em: datetime | None = None
    justificativa: str | None = None
    criado_em: datetime
    atualizado_em: datetime
