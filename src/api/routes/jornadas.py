from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import jornadas as crud
from src.db.session import get_db
from src.schemas.common import MessageResponse
from src.schemas.jornadas import ColaboradorJornadaCreate, ColaboradorJornadaOut, JornadaCreate, JornadaOut, JornadaUpdate, TurnoCreate, TurnoOut

router = APIRouter(prefix="/jornadas", tags=["jornadas"])


@router.get("", response_model=list[JornadaOut])
def listar_jornadas(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "jornadas:view")
    return crud.listar_jornadas(db)


@router.post("", response_model=JornadaOut)
def criar_jornada(payload: JornadaCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "jornadas:create")
    return crud.criar_jornada(db, payload.model_dump(), user.id)


@router.get("/{jornada_id}", response_model=JornadaOut)
def buscar_jornada(jornada_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "jornadas:view")
    return crud.buscar_jornada(db, jornada_id)


@router.patch("/{jornada_id}", response_model=JornadaOut)
def editar_jornada(jornada_id: int, payload: JornadaUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "jornadas:update")
    return crud.editar_jornada(db, jornada_id, payload.model_dump(exclude_none=True), user.id)


@router.delete("/{jornada_id}", response_model=MessageResponse)
def remover_jornada(jornada_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "jornadas:update")
    crud.remover_jornada(db, jornada_id, user.id)
    return {"detail": "Jornada removida com soft delete."}


@router.post("/{jornada_id}/turnos", response_model=TurnoOut)
def criar_turno(jornada_id: int, payload: TurnoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "jornadas:update")
    return crud.criar_turno(db, jornada_id, payload.model_dump(), user.id)


@router.post("/colaboradores/{colaborador_id}", response_model=ColaboradorJornadaOut)
def vincular_colaborador_jornada(colaborador_id: int, payload: ColaboradorJornadaCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "jornadas:update")
    return crud.vincular_jornada_colaborador(db, colaborador_id, payload.model_dump(), user.id)


@router.get("/colaboradores/{colaborador_id}/atual", response_model=ColaboradorJornadaOut | None)
def jornada_atual(colaborador_id: int, data_referencia: date | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "jornadas:view")
    return crud.jornada_atual_colaborador(db, colaborador_id, data_referencia)
