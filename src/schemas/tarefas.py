from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class TarefaCreate(BaseModel):
    titulo: str
    descricao: str | None = None
    modulo: str
    entidade_tipo: str | None = None
    entidade_id: int | None = None
    status: str = "aberta"
    prioridade: str = "media"
    responsavel_id: int | None = None
    solicitante_id: int | None = None
    prazo: datetime | None = None


class TarefaUpdate(BaseModel):
    descricao: str | None = None
    status: str | None = None
    prioridade: str | None = None
    responsavel_id: int | None = None
    prazo: datetime | None = None


class TarefaOut(ORMModel):
    id: int
    titulo: str
    descricao: str | None = None
    modulo: str
    entidade_tipo: str | None = None
    entidade_id: int | None = None
    status: str
    prioridade: str
    responsavel_id: int | None = None
    solicitante_id: int | None = None
    prazo: datetime | None = None
    concluido_em: datetime | None = None
    motivo_cancelamento: str | None = None
    criado_em: datetime
    atualizado_em: datetime


class TarefaComentarioCreate(BaseModel):
    comentario: str


class TarefaComentarioOut(ORMModel):
    id: int
    tarefa_id: int
    usuario_id: int | None = None
    comentario: str
    criado_em: datetime


class TarefaAcao(BaseModel):
    comentario: str | None = None
    responsavel_id: int | None = None
