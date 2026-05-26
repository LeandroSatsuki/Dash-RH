from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import sst as crud
from src.db.session import get_db
from src.schemas.sst import (
    ColaboradorTreinamentoSSTCreate,
    ColaboradorTreinamentoSSTOut,
    EPICreate,
    EPIOut,
    EntregaEPICreate,
    EntregaEPIOut,
    ExameOcupacionalCreate,
    ExameOcupacionalOut,
    TreinamentoSSTCreate,
    TreinamentoSSTOut,
)

router = APIRouter(prefix="/sst", tags=["sst"])


@router.post("/exames", response_model=ExameOcupacionalOut)
def criar_exame(payload: ExameOcupacionalCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "sst:create")
    return crud.criar_exame(db, payload.model_dump(), user.id)


@router.get("/exames", response_model=list[ExameOcupacionalOut])
def listar_exames(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "sst:view")
    return crud.listar_exames(db)


@router.post("/epis", response_model=EPIOut)
def criar_epi(payload: EPICreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "sst:create")
    return crud.criar_epi(db, payload.model_dump(), user.id)


@router.get("/epis", response_model=list[EPIOut])
def listar_epis(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "sst:view")
    return crud.listar_epis(db)


@router.post("/entregas-epi", response_model=EntregaEPIOut)
def criar_entrega(payload: EntregaEPICreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "sst:update")
    return crud.criar_entrega_epi(db, payload.model_dump(), user.id)


@router.get("/entregas-epi", response_model=list[EntregaEPIOut])
def listar_entregas(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "sst:view")
    return crud.listar_entregas_epi(db)


@router.post("/treinamentos", response_model=TreinamentoSSTOut)
def criar_treinamento(payload: TreinamentoSSTCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "sst:create")
    return crud.criar_treinamento(db, payload.model_dump(), user.id)


@router.get("/treinamentos", response_model=list[TreinamentoSSTOut])
def listar_treinamentos(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "sst:view")
    return crud.listar_treinamentos(db)


@router.post("/colaborador-treinamentos", response_model=ColaboradorTreinamentoSSTOut)
def vincular_treinamento(payload: ColaboradorTreinamentoSSTCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "sst:update")
    return crud.vincular_treinamento(db, payload.model_dump(), user.id)


@router.get("/colaborador-treinamentos", response_model=list[ColaboradorTreinamentoSSTOut])
def listar_colaborador_treinamentos(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "sst:view")
    return crud.listar_colaborador_treinamentos(db)
