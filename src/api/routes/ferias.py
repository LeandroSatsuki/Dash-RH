from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import ferias as crud
from src.db.session import get_db
from src.schemas.ferias import FeriasCreate, FeriasOut, FeriasUpdate

router = APIRouter(prefix="/ferias", tags=["ferias"])


@router.get("/", response_model=list[FeriasOut])
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "ferias:view")
    return crud.listar(db)


@router.post("/", response_model=FeriasOut)
def criar(payload: FeriasCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "ferias:create")
    return crud.criar(db, payload.model_dump(), user.id)


@router.put("/{ferias_id}", response_model=FeriasOut)
def editar(ferias_id: int, payload: FeriasUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "ferias:update")
    return crud.editar(db, ferias_id, payload.model_dump(exclude_none=True), user.id)
