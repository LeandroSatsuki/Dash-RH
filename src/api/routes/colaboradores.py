from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import colaboradores as crud
from src.db.session import get_db
from src.schemas.colaboradores import ColaboradorCreate, ColaboradorOut, ColaboradorUpdate

router = APIRouter(prefix="/colaboradores", tags=["colaboradores"])


@router.get("/", response_model=list[ColaboradorOut])
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "colaboradores:view")
    return crud.listar(db)


@router.post("/", response_model=ColaboradorOut)
def criar(payload: ColaboradorCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "colaboradores:create")
    return crud.criar(db, payload.model_dump(), user.id)


@router.get("/{colaborador_id}", response_model=ColaboradorOut)
def buscar(colaborador_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "colaboradores:view")
    return crud.buscar_por_id(db, colaborador_id)


@router.put("/{colaborador_id}", response_model=ColaboradorOut)
def editar(colaborador_id: int, payload: ColaboradorUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "colaboradores:update")
    return crud.editar(db, colaborador_id, payload.model_dump(exclude_none=True), user.id)


@router.delete("/{colaborador_id}")
def remover(colaborador_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "colaboradores:update")
    crud.remover(db, colaborador_id, user.id)
    return {"detail": "Colaborador removido com soft delete."}
