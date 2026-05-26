from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud import tarefas as crud_tarefas
from src.db.models import Tarefa
from src.services.audit_service import log_action
from src.services.notification_service import notify_user
from src.services.workflow_service import sanitize_comment


def create_task(db: Session, data: dict, usuario_id: int | None = None):
    payload = data.copy()
    if payload.get("prioridade") == "critica" and not payload.get("prazo"):
        raise ValueError("Tarefa critica precisa ter prazo.")
    tarefa = crud_tarefas.criar(db, payload, usuario_id)
    if tarefa.responsavel_id:
        notify_user(db, usuario_id=tarefa.responsavel_id, titulo="Tarefa atribuida", mensagem=f"Voce recebeu a tarefa {tarefa.titulo}.", tipo="tarefa_atribuida", severidade="media", link_entidade_tipo="tarefa", link_entidade_id=tarefa.id, origem="tarefas")
    return tarefa


def create_or_get_open_task(
    db: Session,
    *,
    titulo: str,
    modulo: str,
    entidade_tipo: str | None,
    entidade_id: int | None,
    responsavel_id: int | None,
    solicitante_id: int | None,
    prazo: datetime | None,
    prioridade: str = "media",
    descricao: str | None = None,
):
    today = date.today()
    existente = db.scalar(
        select(Tarefa).where(
            Tarefa.deletado_em.is_(None),
            Tarefa.titulo == titulo,
            Tarefa.modulo == modulo,
            Tarefa.entidade_tipo == entidade_tipo,
            Tarefa.entidade_id == entidade_id,
            Tarefa.status.in_(["aberta", "em_andamento", "aguardando_terceiro", "bloqueada"]),
        )
    )
    if existente is not None and existente.criado_em.date() == today:
        return existente
    return create_task(
        db,
        {
            "titulo": titulo,
            "descricao": descricao,
            "modulo": modulo,
            "entidade_tipo": entidade_tipo,
            "entidade_id": entidade_id,
            "responsavel_id": responsavel_id,
            "solicitante_id": solicitante_id,
            "prazo": prazo,
            "prioridade": prioridade,
        },
        solicitante_id,
    )


def update_task(db: Session, tarefa_id: int, data: dict, usuario_id: int | None = None):
    tarefa = crud_tarefas.buscar_por_id(db, tarefa_id)
    if tarefa is None:
        raise ValueError("Tarefa nao encontrada.")
    if data.get("responsavel_id") and data.get("responsavel_id") != tarefa.responsavel_id:
        log_action(db, tabela="tarefas", acao="alterar_responsavel_tarefa", registro_id=tarefa.id, usuario_id=usuario_id, origem="tarefas")
        notify_user(db, usuario_id=data["responsavel_id"], titulo="Tarefa atribuida", mensagem=f"Voce recebeu a tarefa {tarefa.titulo}.", tipo="tarefa_atribuida", severidade="media", link_entidade_tipo="tarefa", link_entidade_id=tarefa.id, origem="tarefas")
    return crud_tarefas.editar(db, tarefa_id, data, usuario_id)


def comment_task(db: Session, tarefa_id: int, comentario: str, usuario_id: int | None = None):
    cleaned = sanitize_comment(comentario)
    return crud_tarefas.criar_comentario(db, tarefa_id, cleaned or "", usuario_id)


def complete_task(db: Session, tarefa_id: int, usuario_id: int | None = None):
    return crud_tarefas.concluir(db, tarefa_id, usuario_id)


def cancel_task(db: Session, tarefa_id: int, motivo: str, usuario_id: int | None = None):
    if not motivo:
        raise ValueError("Tarefa cancelada exige motivo.")
    return crud_tarefas.cancelar(db, tarefa_id, sanitize_comment(motivo) or "", usuario_id)


def overdue_tasks(db: Session):
    now = datetime.now(UTC).replace(tzinfo=None)
    return [item for item in crud_tarefas.listar(db) if item.prazo and item.prazo < now and item.status not in {"concluida", "cancelada"}]
