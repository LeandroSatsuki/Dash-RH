from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import centros_custo as crud
from src.db.session import get_db
from src.schemas.centros_custo import CentroCustoCreate, CentroCustoOut, CentroCustoUpdate

router = APIRouter(prefix="/centros-custo", tags=["centros_custo"])


@router.get("/", response_model=list[CentroCustoOut])
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "centros_custo:view")
    return crud.listar(db)


@router.post("/", response_model=CentroCustoOut)
def criar(payload: CentroCustoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "centros_custo:create")
    return crud.criar(db, payload.model_dump(), user.id)


@router.put("/{centro_custo_id}", response_model=CentroCustoOut)
def editar(centro_custo_id: int, payload: CentroCustoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "centros_custo:update")
    return crud.editar(db, centro_custo_id, payload.model_dump(exclude_none=True), user.id)
