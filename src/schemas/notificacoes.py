from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class NotificacaoCreate(BaseModel):
    usuario_id: int
    titulo: str
    mensagem: str
    tipo: str
    severidade: str = "info"
    link_entidade_tipo: str | None = None
    link_entidade_id: int | None = None


class NotificacaoOut(ORMModel, NotificacaoCreate):
    id: int
    lida: bool
    criado_em: datetime
    lida_em: datetime | None = None
