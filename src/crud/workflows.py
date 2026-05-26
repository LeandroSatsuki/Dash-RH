from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud.base import create_record, list_records, update_record
from src.db.models import Workflow, WorkflowEtapa, WorkflowHistorico, WorkflowInstancia


def criar_workflow(db: Session, data: dict, usuario_id: int | None = None):
    return create_record(db, Workflow, data, usuario_id)


def listar_workflows(db: Session):
    return list_records(db, Workflow)


def buscar_workflow(db: Session, workflow_id: int):
    return db.get(Workflow, workflow_id)


def buscar_workflow_por_modulo(db: Session, modulo: str):
    return db.scalar(select(Workflow).where(Workflow.modulo == modulo, Workflow.ativo.is_(True), Workflow.deletado_em.is_(None)))


def criar_etapa(db: Session, workflow_id: int, data: dict, usuario_id: int | None = None):
    return create_record(db, WorkflowEtapa, {"workflow_id": workflow_id, **data}, usuario_id)


def listar_etapas(db: Session, workflow_id: int):
    stmt = select(WorkflowEtapa).where(WorkflowEtapa.workflow_id == workflow_id, WorkflowEtapa.ativo.is_(True)).order_by(WorkflowEtapa.ordem.asc())
    return list(db.scalars(stmt).all())


def criar_instancia(db: Session, data: dict, usuario_id: int | None = None):
    payload = data.copy()
    payload.setdefault("status", "rascunho")
    return create_record(db, WorkflowInstancia, payload, usuario_id)


def buscar_instancia(db: Session, instancia_id: int):
    return db.get(WorkflowInstancia, instancia_id)


def buscar_instancia_por_entidade(db: Session, entidade_tipo: str, entidade_id: int):
    return db.scalar(
        select(WorkflowInstancia)
        .where(WorkflowInstancia.entidade_tipo == entidade_tipo, WorkflowInstancia.entidade_id == entidade_id)
        .order_by(WorkflowInstancia.criado_em.desc())
    )


def atualizar_instancia(db: Session, instancia, data: dict, usuario_id: int | None = None):
    return update_record(db, instancia, data, usuario_id)


def registrar_historico(db: Session, data: dict):
    historico = WorkflowHistorico(**data)
    db.add(historico)
    db.commit()
    db.refresh(historico)
    return historico


def listar_historico(db: Session, instancia_id: int):
    stmt = select(WorkflowHistorico).where(WorkflowHistorico.instancia_id == instancia_id).order_by(WorkflowHistorico.criado_em.asc())
    return list(db.scalars(stmt).all())
