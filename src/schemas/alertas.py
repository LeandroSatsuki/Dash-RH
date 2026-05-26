from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class AlertaOut(ORMModel):
    id: int
    tipo: str
    severidade: str
    titulo: str
    descricao: str
    entidade_tipo: str | None = None
    entidade_id: int | None = None
    status: str
    resolvido_em: datetime | None = None
    usuario_responsavel_id: int | None = None
    justificativa: str | None = None
    criado_em: datetime
    atualizado_em: datetime


class AlertaAction(BaseModel):
    justificativa: str | None = None
