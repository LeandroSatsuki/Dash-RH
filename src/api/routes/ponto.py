from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import ponto as crud
from src.db.session import get_db
from src.schemas.common import MessageResponse
from src.schemas.ponto import AjustePontoCreate, AjustePontoOut, ApuracaoPontoOut, ApuracaoPontoRequest, MarcacaoPontoCreate, MarcacaoPontoOut
from src.services.importacao_ponto import importar_marcacoes

router = APIRouter(prefix="/ponto", tags=["ponto"])


@router.post("/marcacoes", response_model=MarcacaoPontoOut)
def criar_marcacao(payload: MarcacaoPontoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "ponto:create")
    return crud.criar_marcacao(db, payload.model_dump(), user.id)


@router.get("/marcacoes", response_model=list[MarcacaoPontoOut])
def listar_marcacoes(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "ponto:view")
    return crud.listar_marcacoes(db)


@router.post("/importar")
def importar_ponto(
    arquivo: UploadFile,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    require_permission(user, "ponto:create")
    temp_path = f"data/uploads/{arquivo.filename}"
    with open(temp_path, "wb") as target:
        target.write(arquivo.file.read())
    return importar_marcacoes(
        db,
        path=temp_path,
        column_map={"matricula": "matricula", "cpf": "cpf", "nome": "nome", "data": "data", "entrada": "entrada", "saida_intervalo": "saida_intervalo", "retorno_intervalo": "retorno_intervalo", "saida": "saida"},
        usuario_id=user.id,
        origem="importado_excel" if arquivo.filename.lower().endswith(("xlsx", "xls")) else "importado_csv",
    ).__dict__


@router.post("/apurar", response_model=list[ApuracaoPontoOut])
def apurar(payload: ApuracaoPontoRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "ponto:update")
    return crud.apurar_periodo(db, **payload.model_dump(), usuario_id=user.id)


@router.get("/apuracoes", response_model=list[ApuracaoPontoOut])
def listar_apuracoes(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "ponto:view")
    return crud.listar_apuracoes(db)


@router.post("/ajustes", response_model=AjustePontoOut)
def criar_ajuste(payload: AjustePontoCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "ponto:update")
    return crud.criar_ajuste(db, payload.model_dump(), user.id)


@router.post("/ajustes/{ajuste_id}/aprovar", response_model=AjustePontoOut)
def aprovar_ajuste(ajuste_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "ponto:approve")
    return crud.aprovar_ajuste(db, ajuste_id, user.id)


@router.post("/ajustes/{ajuste_id}/reprovar", response_model=AjustePontoOut)
def reprovar_ajuste(ajuste_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "ponto:approve")
    return crud.reprovar_ajuste(db, ajuste_id, user.id)


@router.get("/resumo/{colaborador_id}")
def resumo_colaborador(colaborador_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "ponto:view")
    return crud.resumo_por_colaborador(db, colaborador_id)


@router.get("/resumo-departamento")
def resumo_departamento(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "ponto:view")
    return crud.resumo_por_departamento(db)
