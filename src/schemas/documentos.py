from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class DocumentoBase(BaseModel):
    colaborador_id: int
    tipo_documento: str
    nome_original: str
    nome_armazenado: str
    caminho_arquivo: str
    hash_arquivo: str
    validade: date | None = None
    status: str = "ativo"
    usuario_upload_id: int | None = None


class DocumentoCreate(DocumentoBase):
    pass


class DocumentoUpdate(BaseModel):
    tipo_documento: str | None = None
    validade: date | None = None
    status: str | None = None


class DocumentoOut(ORMModel, DocumentoBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
