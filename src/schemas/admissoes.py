from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class AdmissaoBase(BaseModel):
    colaborador_id: int
    data_prevista_admissao: date | None = None
    data_admissao: date | None = None
    status: str = "rascunho"
    checklist_json: dict | None = None
    observacao: str | None = None


class AdmissaoCreate(AdmissaoBase):
    pass


class AdmissaoUpdate(BaseModel):
    data_prevista_admissao: date | None = None
    data_admissao: date | None = None
    status: str | None = None
    checklist_json: dict | None = None
    observacao: str | None = None


class AdmissaoOut(ORMModel, AdmissaoBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime
