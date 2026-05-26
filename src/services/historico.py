from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import HistoricoFuncional


def registrar_historico(
    db: Session,
    *,
    colaborador_id: int,
    tipo_evento: str,
    data_evento: date,
    usuario_id: int | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    campo_alterado: str | None = None,
    valor_anterior: Any = None,
    valor_novo: Any = None,
    motivo: str | None = None,
) -> HistoricoFuncional:
    evento = HistoricoFuncional(
        colaborador_id=colaborador_id,
        tipo_evento=tipo_evento,
        data_evento=data_evento,
        data_inicio=data_inicio,
        data_fim=data_fim,
        campo_alterado=campo_alterado,
        valor_anterior=None if valor_anterior is None else str(valor_anterior),
        valor_novo=None if valor_novo is None else str(valor_novo),
        motivo=motivo,
        usuario_id=usuario_id,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


def listar_historico_colaborador(db: Session, colaborador_id: int) -> list[HistoricoFuncional]:
    stmt = (
        select(HistoricoFuncional)
        .where(HistoricoFuncional.colaborador_id == colaborador_id)
        .order_by(HistoricoFuncional.data_evento.desc(), HistoricoFuncional.criado_em.desc())
    )
    return list(db.scalars(stmt).all())
