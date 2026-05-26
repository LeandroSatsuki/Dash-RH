from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import documentos_obrigatorios as crud
from src.db.session import get_db
from src.schemas.alertas import AlertaAction
from src.schemas.documentos_obrigatorios import (
    DocumentoObrigatorioRegraCreate,
    DocumentoObrigatorioRegraOut,
    DocumentoPendenciaOut,
    TipoDocumentoCreate,
    TipoDocumentoOut,
)

router = APIRouter(prefix="/documentos", tags=["documentos_obrigatorios"])


@router.post("/tipos", response_model=TipoDocumentoOut)
def criar_tipo(payload: TipoDocumentoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "documentos_obrigatorios:update")
    return crud.criar_tipo_documento(db, payload.model_dump(), user.id)


@router.get("/tipos", response_model=list[TipoDocumentoOut])
def listar_tipos(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "documentos_obrigatorios:view")
    return crud.listar_tipos_documento(db)


@router.post("/regras", response_model=DocumentoObrigatorioRegraOut)
def criar_regra(payload: DocumentoObrigatorioRegraCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "documentos_obrigatorios:update")
    return crud.criar_regra(db, payload.model_dump(), user.id)


@router.get("/regras", response_model=list[DocumentoObrigatorioRegraOut])
def listar_regras(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "documentos_obrigatorios:view")
    return crud.listar_regras(db)


@router.post("/gerar-pendencias", response_model=list[DocumentoPendenciaOut])
def gerar_pendencias(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "documentos_obrigatorios:update")
    return crud.gerar_pendencias(db, user.id)


@router.get("/pendencias", response_model=list[DocumentoPendenciaOut])
def listar_pendencias(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "documentos_obrigatorios:view")
    return crud.listar_pendencias(db)


@router.post("/pendencias/{pendencia_id}/aprovar", response_model=DocumentoPendenciaOut)
def aprovar_pendencia(pendencia_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "documentos_obrigatorios:update")
    return crud.aprovar_pendencia(db, pendencia_id, user.id)


@router.post("/pendencias/{pendencia_id}/dispensar", response_model=DocumentoPendenciaOut)
def dispensar_pendencia(pendencia_id: int, payload: AlertaAction, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "documentos_obrigatorios:update")
    return crud.dispensar_pendencia(db, pendencia_id, payload.justificativa or "Dispensado operacionalmente.", user.id)
