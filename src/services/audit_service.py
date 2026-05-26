from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Auditoria
from src.services.masking import mask_cnpj, mask_cpf

SENSITIVE_KEYS = {"senha", "password", "senha_hash", "token", "access_token", "secret_key"}
MASKED_KEYS = {"cpf", "cnpj", "cpf_cnpj", "documento", "cid", "email", "telefone", "salario", "salario_base", "valor", "valor_empresa", "valor_colaborador"}


def _sanitize_key_value(key: str, value: Any) -> Any:
    normalized = key.lower()
    if normalized in SENSITIVE_KEYS:
        return "[REDACTED]"
    if value is None:
        return None
    if normalized == "cpf":
        return mask_cpf(str(value))
    if normalized == "cnpj":
        return mask_cnpj(str(value))
    if normalized in {"documento", "cid"}:
        return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]
    if normalized in MASKED_KEYS:
        return "[MASKED]"
    return value


def sanitize_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {str(key): _sanitize_key_value(str(key), sanitize_payload(value)) for key, value in payload.items()}
    if isinstance(payload, list):
        return [sanitize_payload(item) for item in payload]
    return payload


def compare_changes(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    changes = []
    for key in sorted(set(before.keys()) | set(after.keys())):
        old = before.get(key)
        new = after.get(key)
        if old != new:
            changes.append(
                {
                    "campo": key,
                    "valor_anterior": _sanitize_key_value(key, old),
                    "valor_novo": _sanitize_key_value(key, new),
                }
            )
    return changes


def log_action(
    db: Session,
    *,
    tabela: str,
    acao: str,
    registro_id: int | None = None,
    usuario_id: int | None = None,
    origem: str | None = None,
    ip: str | None = None,
    campo_alterado: str | None = None,
    valor_anterior: Any = None,
    valor_novo: Any = None,
) -> Auditoria:
    evento = Auditoria(
        usuario_id=usuario_id,
        tabela=tabela,
        registro_id=registro_id,
        acao=acao,
        campo_alterado=campo_alterado,
        valor_anterior=None if valor_anterior is None else json.dumps(sanitize_payload(valor_anterior), ensure_ascii=False, default=str),
        valor_novo=None if valor_novo is None else json.dumps(sanitize_payload(valor_novo), ensure_ascii=False, default=str),
        origem=origem,
        ip=ip,
        criado_em=datetime.now(UTC).replace(tzinfo=None),
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


def list_audit_logs(
    db: Session,
    *,
    usuario_id: int | None = None,
    tabela: str | None = None,
    acao: str | None = None,
    registro_id: int | None = None,
    data_inicio: datetime | None = None,
    data_fim: datetime | None = None,
) -> list[Auditoria]:
    stmt = select(Auditoria)
    if usuario_id is not None:
        stmt = stmt.where(Auditoria.usuario_id == usuario_id)
    if tabela:
        stmt = stmt.where(Auditoria.tabela == tabela)
    if acao:
        stmt = stmt.where(Auditoria.acao == acao)
    if registro_id is not None:
        stmt = stmt.where(Auditoria.registro_id == registro_id)
    if data_inicio is not None:
        stmt = stmt.where(Auditoria.criado_em >= data_inicio)
    if data_fim is not None:
        stmt = stmt.where(Auditoria.criado_em <= data_fim)
    stmt = stmt.order_by(Auditoria.criado_em.desc())
    return list(db.scalars(stmt).all())


def log_sensitive_view(
    db: Session,
    *,
    tabela: str,
    registro_id: int | None,
    usuario_id: int | None,
    campos: list[str],
    origem: str | None = None,
    ip: str | None = None,
) -> Auditoria:
    return log_action(
        db,
        tabela=tabela,
        acao="view_sensitive_data",
        registro_id=registro_id,
        usuario_id=usuario_id,
        origem=origem,
        ip=ip,
        valor_novo={"campos": campos},
    )
