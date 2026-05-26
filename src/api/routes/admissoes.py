from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import admissoes as crud
from src.db.session import get_db
from src.schemas.admissoes import AdmissaoCreate, AdmissaoOut, AdmissaoUpdate

router = APIRouter(prefix="/admissoes", tags=["admissoes"])


@router.get("/", response_model=list[AdmissaoOut])
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "admissoes:view")
    return crud.listar(db)


@router.post("/", response_model=AdmissaoOut)
def criar(payload: AdmissaoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "admissoes:create")
    return crud.criar(db, payload.model_dump(), user.id)


@router.get("/{admissao_id}", response_model=AdmissaoOut)
def buscar(admissao_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "admissoes:view")
    return crud.buscar_por_id(db, admissao_id)


@router.patch("/{admissao_id}", response_model=AdmissaoOut)
def editar(admissao_id: int, payload: AdmissaoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "admissoes:update")
    return crud.editar(db, admissao_id, payload.model_dump(exclude_none=True), user.id)


@router.post("/{admissao_id}/concluir", response_model=AdmissaoOut)
def concluir(admissao_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "admissoes:update")
    return crud.concluir(db, admissao_id, user.id)


@router.post("/{admissao_id}/cancelar", response_model=AdmissaoOut)
def cancelar(admissao_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "admissoes:update")
    return crud.cancelar(db, admissao_id, user.id)
