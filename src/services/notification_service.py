from __future__ import annotations

import re
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from src.crud import notificacoes as crud_notificacoes
from src.services.audit_service import log_action


def sanitize_message(text: str | None) -> str:
    if not text:
        return ""
    sanitized = re.sub(r"\b\d{11}\b", "[CPF_MASKED]", str(text))
    sanitized = re.sub(r"R\$\s?\d[\d\.,]*", "R$ [MASKED]", sanitized)
    sanitized = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[EMAIL_MASKED]", sanitized)
    return sanitized[:1000]


def notify_user(
    db: Session,
    *,
    usuario_id: int,
    titulo: str,
    mensagem: str,
    tipo: str,
    severidade: str = "info",
    link_entidade_tipo: str | None = None,
    link_entidade_id: int | None = None,
    origem: str = "notificacoes",
) -> object:
    notificacao = crud_notificacoes.criar(
        db,
        {
            "usuario_id": usuario_id,
            "titulo": sanitize_message(titulo),
            "mensagem": sanitize_message(mensagem),
            "tipo": tipo,
            "severidade": severidade,
            "link_entidade_tipo": link_entidade_tipo,
            "link_entidade_id": link_entidade_id,
        },
        usuario_id,
    )
    log_action(db, tabela="notificacoes", acao="criar_notificacao", registro_id=notificacao.id, usuario_id=usuario_id, origem=origem)
    return notificacao


def notify_many(db: Session, usuarios_ids: list[int], **kwargs):
    itens = []
    for usuario_id in usuarios_ids:
        itens.append(notify_user(db, usuario_id=usuario_id, **kwargs))
    return itens


def marcar_lida(db: Session, notificacao_id: int, usuario_id: int):
    notificacao = crud_notificacoes.marcar_lida(db, notificacao_id, usuario_id)
    log_action(db, tabela="notificacoes", acao="marcar_lida", registro_id=notificacao.id, usuario_id=usuario_id, origem="notificacoes")
    return notificacao


def marcar_todas_lidas(db: Session, usuario_id: int):
    total = crud_notificacoes.marcar_todas_lidas(db, usuario_id)
    log_action(db, tabela="notificacoes", acao="marcar_todas_lidas", usuario_id=usuario_id, origem="notificacoes", valor_novo={"total": total})
    return total


def unread_count(db: Session, usuario_id: int) -> int:
    return len(crud_notificacoes.listar(db, usuario_id=usuario_id, apenas_nao_lidas=True))
