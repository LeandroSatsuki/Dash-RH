from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.crud import notificacoes as crud
from src.db.session import get_db
from src.schemas.notificacoes import NotificacaoOut
from src.services import notification_service

router = APIRouter(prefix="/notificacoes", tags=["notificacoes"])


@router.get("", response_model=list[NotificacaoOut])
def listar_notificacoes(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "notificacoes:view")
    return crud.listar(db, usuario_id=user.id)


@router.post("/{notificacao_id}/lida", response_model=NotificacaoOut)
def marcar_lida(notificacao_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "notificacoes:update")
    return notification_service.marcar_lida(db, notificacao_id, user.id)


@router.post("/lidas")
def marcar_todas_lidas(db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "notificacoes:update")
    return {"total": notification_service.marcar_todas_lidas(db, user.id)}
