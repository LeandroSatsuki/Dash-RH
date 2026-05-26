from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.permissions import require_permission
from src.db.session import get_db
from src.services.indicadores import indicadores_dashboard

router = APIRouter(prefix="/indicadores", tags=["indicadores"])


@router.get("/")
def obter_indicadores(competencia: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_permission(user, "indicadores:view")
    return indicadores_dashboard(db, competencia)
