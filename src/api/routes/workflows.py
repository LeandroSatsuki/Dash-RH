from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import workflows as crud
from src.db.models import WorkflowInstancia
from src.db.session import get_db
from src.schemas.workflows import WorkflowAction, WorkflowCreate, WorkflowEtapaCreate, WorkflowEtapaOut, WorkflowInstanciaOut, WorkflowOut
from src.services import workflow_service

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("", response_model=list[WorkflowOut])
def listar_workflows(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "workflows:view")
    return crud.listar_workflows(db)


@router.post("", response_model=WorkflowOut)
def criar_workflow(payload: WorkflowCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "workflows:create")
    return crud.criar_workflow(db, payload.model_dump(), user.id)


@router.post("/{workflow_id}/etapas", response_model=WorkflowEtapaOut)
def criar_etapa(workflow_id: int, payload: WorkflowEtapaCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "workflows:update")
    return crud.criar_etapa(db, workflow_id, payload.model_dump(), user.id)


@router.get("/instancias", response_model=list[WorkflowInstanciaOut])
def listar_instancias(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "workflows:view")
    return list(db.query(WorkflowInstancia).all())


@router.post("/instancias/{instancia_id}/aprovar", response_model=WorkflowInstanciaOut)
def aprovar(instancia_id: int, payload: WorkflowAction, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "workflows:approve")
    return workflow_service.approve_instance(db, instancia_id, user.id, payload.comentario)


@router.post("/instancias/{instancia_id}/reprovar", response_model=WorkflowInstanciaOut)
def reprovar(instancia_id: int, payload: WorkflowAction, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "workflows:approve")
    return workflow_service.reject_instance(db, instancia_id, user.id, payload.comentario or "")


@router.post("/instancias/{instancia_id}/devolver", response_model=WorkflowInstanciaOut)
def devolver(instancia_id: int, payload: WorkflowAction, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "workflows:update")
    return workflow_service.return_instance(db, instancia_id, user.id, payload.comentario or "")


@router.post("/instancias/{instancia_id}/responsavel", response_model=WorkflowInstanciaOut)
def reatribuir(instancia_id: int, payload: WorkflowAction, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "workflows:update")
    if payload.responsavel_id is None:
        raise ValueError("responsavel_id obrigatorio.")
    return workflow_service.reassign_instance(db, instancia_id, payload.responsavel_id, user.id, payload.comentario)
