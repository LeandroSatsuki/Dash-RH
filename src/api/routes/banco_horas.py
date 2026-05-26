from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import banco_horas as crud
from src.db.session import get_db
from src.schemas.banco_horas import BancoHorasMovimentoCreate, BancoHorasMovimentoOut

router = APIRouter(prefix="/banco-horas", tags=["banco_horas"])


@router.get("/movimentos", response_model=list[BancoHorasMovimentoOut])
def listar_movimentos(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "banco_horas:view")
    return crud.listar_movimentos(db)


@router.post("/movimentos", response_model=BancoHorasMovimentoOut)
def criar_movimento(payload: BancoHorasMovimentoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "banco_horas:update")
    return crud.criar_movimento(db, payload.model_dump(), user.id)


@router.get("/saldo/{colaborador_id}")
def saldo_colaborador(colaborador_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "banco_horas:view")
    return {"colaborador_id": colaborador_id, "saldo": float(crud.saldo_colaborador(db, colaborador_id))}


@router.get("/saldo-departamento")
def saldo_departamento(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "banco_horas:view")
    return crud.saldo_por_departamento(db)
