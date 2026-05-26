from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import cargos as crud
from src.db.session import get_db
from src.schemas.cargos import CargoCreate, CargoOut, CargoUpdate

router = APIRouter(prefix="/cargos", tags=["cargos"])


@router.get("/", response_model=list[CargoOut])
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "cargos:view")
    return crud.listar(db)


@router.post("/", response_model=CargoOut)
def criar(payload: CargoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "cargos:create")
    return crud.criar(db, payload.model_dump(), user.id)


@router.put("/{cargo_id}", response_model=CargoOut)
def editar(cargo_id: int, payload: CargoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "cargos:update")
    return crud.editar(db, cargo_id, payload.model_dump(exclude_none=True), user.id)
