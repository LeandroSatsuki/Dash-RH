from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import tarefas as crud
from src.db.session import get_db
from src.schemas.tarefas import TarefaAcao, TarefaComentarioCreate, TarefaComentarioOut, TarefaCreate, TarefaOut, TarefaUpdate
from src.services import task_service

router = APIRouter(prefix="/tarefas", tags=["tarefas"])


@router.get("", response_model=list[TarefaOut])
def listar_tarefas(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "tarefas:view")
    return crud.listar(db)


@router.post("", response_model=TarefaOut)
def criar_tarefa(payload: TarefaCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "tarefas:create")
    return task_service.create_task(db, payload.model_dump(), user.id)


@router.patch("/{tarefa_id}", response_model=TarefaOut)
def editar_tarefa(tarefa_id: int, payload: TarefaUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "tarefas:update")
    return task_service.update_task(db, tarefa_id, payload.model_dump(exclude_none=True), user.id)


@router.post("/{tarefa_id}/comentarios", response_model=TarefaComentarioOut)
def comentar_tarefa(tarefa_id: int, payload: TarefaComentarioCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "tarefas:comment")
    return task_service.comment_task(db, tarefa_id, payload.comentario, user.id)


@router.post("/{tarefa_id}/concluir", response_model=TarefaOut)
def concluir_tarefa(tarefa_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "tarefas:update")
    return task_service.complete_task(db, tarefa_id, user.id)


@router.post("/{tarefa_id}/cancelar", response_model=TarefaOut)
def cancelar_tarefa(tarefa_id: int, payload: TarefaAcao, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "tarefas:update")
    return task_service.cancel_task(db, tarefa_id, payload.comentario or "", user.id)
