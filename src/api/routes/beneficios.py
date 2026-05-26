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


@router.patch("/{beneficio_id}", response_model=BeneficioOut)
def editar(beneficio_id: int, payload: BeneficioUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "beneficios:update")
    return crud.editar(db, beneficio_id, payload.model_dump(exclude_none=True), user.id)


@router.post("/vinculos", response_model=ColaboradorBeneficioOut)
def vincular(payload: ColaboradorBeneficioCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "beneficios:update")
    return crud.vincular_ao_colaborador(db, payload.model_dump(), user.id)


@router.patch("/vinculos/{vinculo_id}", response_model=ColaboradorBeneficioOut)
def editar_vinculo(vinculo_id: int, payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "beneficios:update")
    return crud.editar_vinculo(db, vinculo_id, payload, user.id)


@router.post("/vinculos/{vinculo_id}/encerrar", response_model=ColaboradorBeneficioOut)
def encerrar_vinculo(vinculo_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "beneficios:update")
    return crud.encerrar_vinculo(db, vinculo_id, user.id)
