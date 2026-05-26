from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class WorkflowCreate(BaseModel):
    nome: str
    modulo: str
    descricao: str | None = None
    ativo: bool = True


class WorkflowOut(ORMModel, WorkflowCreate):
    id: int
    criado_em: datetime
    atualizado_em: datetime
    deletado_em: datetime | None = None


class WorkflowEtapaCreate(BaseModel):
    nome: str
    ordem: int
    perfil_responsavel: str | None = None
    permissao_requerida: str | None = None
    obrigatoria: bool = True
    prazo_horas: int | None = None
    permite_reprovar: bool = True
    permite_devolver: bool = True
    ativo: bool = True


class WorkflowEtapaOut(ORMModel, WorkflowEtapaCreate):
    id: int
    workflow_id: int
    criado_em: datetime
    atualizado_em: datetime


class WorkflowInstanciaCreate(BaseModel):
    workflow_id: int
    entidade_tipo: str
    entidade_id: int
    solicitante_id: int | None = None
    responsavel_atual_id: int | None = None


class WorkflowInstanciaOut(ORMModel):
    id: int
    workflow_id: int
    entidade_tipo: str
    entidade_id: int
    status: str
    etapa_atual_id: int | None = None
    solicitante_id: int | None = None
    responsavel_atual_id: int | None = None
    criado_em: datetime
    atualizado_em: datetime
    concluido_em: datetime | None = None
    cancelado_em: datetime | None = None


class WorkflowAction(BaseModel):
    comentario: str | None = None
    responsavel_id: int | None = None
