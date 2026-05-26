from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import departamentos as crud
from src.db.session import get_db
from src.schemas.departamentos import DepartamentoCreate, DepartamentoOut, DepartamentoUpdate

router = APIRouter(prefix="/departamentos", tags=["departamentos"])


@router.get("/", response_model=list[DepartamentoOut])
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "departamentos:view")
    return crud.listar(db)


@router.post("/", response_model=DepartamentoOut)
def criar(payload: DepartamentoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "departamentos:create")
    return crud.criar(db, payload.model_dump(), user.id)


@router.get("/{departamento_id}", response_model=DepartamentoOut)
def buscar(departamento_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "departamentos:view")
    return crud.buscar_por_id(db, departamento_id)


@router.put("/{departamento_id}", response_model=DepartamentoOut)
def editar(departamento_id: int, payload: DepartamentoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "departamentos:update")
    return crud.editar(db, departamento_id, payload.model_dump(exclude_none=True), user.id)


@router.delete("/{departamento_id}")
def remover(departamento_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "departamentos:delete")
    crud.remover(db, departamento_id, user.id)
    return {"detail": "Departamento removido com soft delete."}
