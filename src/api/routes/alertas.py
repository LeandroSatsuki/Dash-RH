from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.db.session import get_db
from src.schemas.alertas import AlertaAction, AlertaOut
from src.services import alerts

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get("", response_model=list[AlertaOut])
def listar_alertas(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "alertas:view")
    return alerts.listar_alertas(db)


@router.post("/gerar", response_model=list[AlertaOut])
def gerar_alertas(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "alertas:update")
    return alerts.gerar_alertas(db)


@router.post("/{alerta_id}/resolver", response_model=AlertaOut)
def resolver_alerta(alerta_id: int, payload: AlertaAction, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "alertas:update")
    return alerts.resolver_alerta(db, alerta_id, user.id, payload.justificativa)


@router.post("/{alerta_id}/ignorar", response_model=AlertaOut)
def ignorar_alerta(alerta_id: int, payload: AlertaAction, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "alertas:update")
    return alerts.ignorar_alerta(db, alerta_id, user.id, payload.justificativa)
