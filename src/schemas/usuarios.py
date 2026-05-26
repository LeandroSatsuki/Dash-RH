from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from src.schemas.common import ORMModel


class UsuarioLogin(BaseModel):
    email: str
    senha: str


class UsuarioOut(ORMModel):
    id: int
    nome: str
    email: str
    perfil: str
    ativo: bool
    criado_em: datetime
