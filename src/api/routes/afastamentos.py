from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import afastamentos as crud
from src.db.session import get_db
from src.schemas.afastamentos import AfastamentoCreate, AfastamentoOut, AfastamentoUpdate

router = APIRouter(prefix="/afastamentos", tags=["afastamentos"])


@router.get("/", response_model=list[AfastamentoOut])
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "afastamentos:view")
    return crud.listar(db)


@router.post("/", response_model=AfastamentoOut)
def criar(payload: AfastamentoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "afastamentos:create")
    return crud.criar(db, payload.model_dump(), user.id)


@router.put("/{afastamento_id}", response_model=AfastamentoOut)
def editar(afastamento_id: int, payload: AfastamentoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "afastamentos:update")
    return crud.editar(db, afastamento_id, payload.model_dump(exclude_none=True), user.id)
