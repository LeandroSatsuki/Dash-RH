from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import beneficios as crud
from src.db.session import get_db
from src.schemas.beneficios import BeneficioCreate, BeneficioOut, BeneficioUpdate, ColaboradorBeneficioCreate, ColaboradorBeneficioOut

router = APIRouter(prefix="/beneficios", tags=["beneficios"])


@router.get("/", response_model=list[BeneficioOut])
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "beneficios:view")
    return crud.listar(db)


@router.post("/", response_model=BeneficioOut)
def criar(payload: BeneficioCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "beneficios:create")
    return crud.criar(db, payload.model_dump(), user.id)


@router.post("/vinculos", response_model=ColaboradorBeneficioOut)
def vincular(payload: ColaboradorBeneficioCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "beneficios:update")
    return crud.vincular_ao_colaborador(db, payload.model_dump(), user.id)
