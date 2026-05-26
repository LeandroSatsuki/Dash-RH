from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.auth.security import create_access_token
from src.auth.users import authenticate_user
from src.db.session import get_db
from src.schemas.usuarios import UsuarioLogin, UsuarioOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(payload: UsuarioLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.senha)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")
    token = create_access_token({"user_id": user.id, "perfil": user.perfil, "email": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UsuarioOut)
def me(user=Depends(get_current_user)):
    return user
