from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from src.crud import workflows as crud_workflows
from src.db.models import Afastamento, ColaboradorTreinamentoSST, DocumentoPendencia, ExameOcupacional, Ferias
from src.services import alerts
from src.services.notification_service import notify_user
from src.services.task_service import create_or_get_open_task, overdue_tasks


def run_daily_checks(db: Session, usuario_sistema_id: int = 1) -> dict:
    now = datetime.now(UTC).replace(tzinfo=None)
    created = 0
    for item in db.query(DocumentoPendencia).filter(DocumentoPendencia.status.in_(["pendente", "vencido"])).all():
        tarefa = create_or_get_open_task(
            db,
            titulo=f"Regularizar documento {item.id}",
            modulo="documentos",
            entidade_tipo="documento_pendencia",
            entidade_id=item.id,
            responsavel_id=usuario_sistema_id,
            solicitante_id=usuario_sistema_id,
            prazo=now + timedelta(days=2),
            prioridade="alta" if item.status == "vencido" else "media",
            descricao=f"Documento do colaborador {item.colaborador_id} precisa de tratamento.",
        )
        created += 1 if tarefa is not None else 0
    for item in db.query(ExameOcupacional).all():
        if item.data_validade and item.data_validade < now.date():
            create_or_get_open_task(
                db,
                titulo=f"Renovar exame {item.id}",
                modulo="sst",
                entidade_tipo="exame_ocupacional",
                entidade_id=item.id,
                responsavel_id=usuario_sistema_id,
                solicitante_id=usuario_sistema_id,
                prazo=now + timedelta(days=2),
                prioridade="alta",
                descricao=f"Exame vencido do colaborador {item.colaborador_id}.",
            )
            created += 1
    for item in db.query(ColaboradorTreinamentoSST).all():
        if item.data_validade and item.data_validade < now.date():
            create_or_get_open_task(
                db,
                titulo=f"Atualizar treinamento {item.id}",
                modulo="sst",
                entidade_tipo="colaborador_treinamento_sst",
                entidade_id=item.id,
                responsavel_id=usuario_sistema_id,
                solicitante_id=usuario_sistema_id,
                prazo=now + timedelta(days=3),
                prioridade="media",
                descricao=f"Treinamento vencido do colaborador {item.colaborador_id}.",
            )
            created += 1
    for item in db.query(Ferias).all():
        if item.data_limite_gozo and item.data_limite_gozo < now.date() and item.status != "concluida":
            create_or_get_open_task(
                db,
                titulo=f"Tratar ferias {item.id}",
                modulo="ferias",
                entidade_tipo="ferias",
                entidade_id=item.id,
                responsavel_id=usuario_sistema_id,
                solicitante_id=usuario_sistema_id,
                prazo=now + timedelta(days=1),
                prioridade="alta",
                descricao=f"Ferias vencidas do colaborador {item.colaborador_id}.",
            )
            created += 1
    for item in alerts.gerar_alertas(db):
        if item.severidade == "critica":
            notify_user(db, usuario_id=usuario_sistema_id, titulo="Alerta critico", mensagem=item.titulo, tipo="alerta_critico", severidade="critica", link_entidade_tipo=item.entidade_tipo, link_entidade_id=item.entidade_id, origem="daily_checks")
    for task in overdue_tasks(db):
        if task.responsavel_id:
            notify_user(db, usuario_id=task.responsavel_id, titulo="Tarefa vencida", mensagem=f"A tarefa {task.titulo} esta vencida.", tipo="tarefa_vencida", severidade="alta", link_entidade_tipo="tarefa", link_entidade_id=task.id, origem="daily_checks")
    return {"tarefas_processadas": created, "alertas": len(alerts.listar_alertas(db))}
