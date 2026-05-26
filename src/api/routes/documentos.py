from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import documentos as crud
from src.db.session import get_db
from src.schemas.documentos import DocumentoCreate, DocumentoOut, DocumentoUpdate

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.get("/", response_model=list[DocumentoOut])
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.perfil in {"auditor", "rh"}:
        require_permission(user, "documentos:view_limited")
    else:
        require_permission(user, "documentos:view")
    return crud.listar(db)


@router.post("/", response_model=DocumentoOut)
def criar(payload: DocumentoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "documentos:create")
    return crud.criar(db, payload.model_dump(), user.id)


@router.put("/{documento_id}", response_model=DocumentoOut)
def editar(documento_id: int, payload: DocumentoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "documentos:update")
    return crud.editar(db, documento_id, payload.model_dump(exclude_none=True), user.id)
