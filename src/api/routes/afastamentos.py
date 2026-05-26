from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import afastamentos as crud
from src.db.session import get_db
from src.schemas.afastamentos import AfastamentoCreate, AfastamentoOut, AfastamentoUpdate

router = APIRouter(prefix="/afastamentos", tags=["afastamentos"])


@router.get("/", response_model=list[AfastamentoOut])
def listar(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "afastamentos:view")
    return crud.listar(db)


@router.post("/", response_model=AfastamentoOut)
def criar(payload: AfastamentoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "afastamentos:create")
    return crud.criar(db, payload.model_dump(), user.id)


@router.get("/{afastamento_id}", response_model=AfastamentoOut)
def buscar(afastamento_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "afastamentos:view")
    return crud.buscar_por_id(db, afastamento_id)


@router.patch("/{afastamento_id}", response_model=AfastamentoOut)
def editar(afastamento_id: int, payload: AfastamentoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "afastamentos:update")
    return crud.editar(db, afastamento_id, payload.model_dump(exclude_none=True), user.id)


@router.post("/{afastamento_id}/encerrar", response_model=AfastamentoOut)
def encerrar(afastamento_id: int, data_fim: date, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "afastamentos:update")
    return crud.encerrar(db, afastamento_id, data_fim, user.id)


@router.post("/{afastamento_id}/anexar-documento")
async def anexar_documento(afastamento_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "documentos:create")
    content = await file.read()
    return crud.anexar_documento(db, afastamento_id=afastamento_id, original_name=file.filename or "documento.pdf", content=content, usuario_id=user.id)
