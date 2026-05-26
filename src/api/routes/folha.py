from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import folha as crud
from src.db.session import get_db
from src.schemas.folha import (
    CompetenciaFolhaCreate,
    CompetenciaFolhaOut,
    CompetenciaFolhaUpdate,
    LancamentoFolhaCreate,
    LancamentoFolhaOut,
    LancamentoFolhaUpdate,
    RubricaCreate,
    RubricaOut,
    RubricaUpdate,
)

router = APIRouter(prefix="/folha", tags=["folha"])


@router.get("/competencias", response_model=list[CompetenciaFolhaOut])
def listar_competencias(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "folha:view")
    return crud.listar_competencias(db)


@router.post("/competencias", response_model=CompetenciaFolhaOut)
def criar_competencia(payload: CompetenciaFolhaCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "folha:create")
    return crud.criar_competencia(db, payload.model_dump(), user.id)


@router.put("/competencias/{competencia_id}", response_model=CompetenciaFolhaOut)
def editar_competencia(competencia_id: int, payload: CompetenciaFolhaUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "folha:update")
    return crud.editar_competencia(db, competencia_id, payload.model_dump(exclude_none=True), user.id)


@router.post("/competencias/{competencia_id}/fechar", response_model=CompetenciaFolhaOut)
def fechar_competencia(competencia_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "folha:update")
    return crud.fechar_competencia(db, competencia_id, user.id)


@router.post("/competencias/{competencia_id}/reabrir", response_model=CompetenciaFolhaOut)
def reabrir_competencia(competencia_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "folha:update")
    return crud.reabrir_competencia(db, competencia_id, user.id)


@router.get("/rubricas", response_model=list[RubricaOut])
def listar_rubricas(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "folha:view")
    return crud.listar_rubricas(db)


@router.post("/rubricas", response_model=RubricaOut)
def criar_rubrica(payload: RubricaCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "folha:create")
    return crud.criar_rubrica(db, payload.model_dump(), user.id)


@router.put("/rubricas/{rubrica_id}", response_model=RubricaOut)
def editar_rubrica(rubrica_id: int, payload: RubricaUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "folha:update")
    return crud.editar_rubrica(db, rubrica_id, payload.model_dump(exclude_none=True), user.id)


@router.get("/lancamentos", response_model=list[LancamentoFolhaOut])
def listar_lancamentos(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "folha:view")
    return crud.listar_lancamentos(db)


@router.post("/lancamentos", response_model=LancamentoFolhaOut)
def criar_lancamento(payload: LancamentoFolhaCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "folha:create")
    return crud.criar_lancamento(db, payload.model_dump(), user.id)


@router.put("/lancamentos/{lancamento_id}", response_model=LancamentoFolhaOut)
def editar_lancamento(lancamento_id: int, payload: LancamentoFolhaUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "folha:update")
    return crud.editar_lancamento(db, lancamento_id, payload.model_dump(exclude_none=True), user.id)
