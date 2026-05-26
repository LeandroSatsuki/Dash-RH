from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import desligamentos as crud
from src.db.session import get_db
from src.schemas.common import MessageResponse

router = APIRouter(prefix="/desligamentos", tags=["desligamentos"])


@router.get("/")
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "desligamentos:view")
    return crud.listar(db)


@router.post("/")
def criar(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "desligamentos:create")
    return crud.criar(db, payload, user.id)


@router.get("/{desligamento_id}")
def buscar(desligamento_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "desligamentos:view")
    return crud.buscar_por_id(db, desligamento_id)


@router.patch("/{desligamento_id}")
def editar(desligamento_id: int, payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "desligamentos:update")
    return crud.editar(db, desligamento_id, payload, user.id)


@router.post("/{desligamento_id}/concluir")
def concluir(desligamento_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "desligamentos:update")
    return crud.concluir(db, desligamento_id, user.id)


@router.post("/{desligamento_id}/cancelar")
def cancelar(desligamento_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "desligamentos:update")
    return crud.cancelar(db, desligamento_id, user.id)
