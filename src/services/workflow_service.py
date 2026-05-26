from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.auth.permissions import has_permission
from src.crud import workflows as crud_workflows
from src.db.models import Usuario, WorkflowEtapa
from src.services.audit_service import log_action
from src.services.notification_service import notify_user

FINAL_STATUSES = {"aprovado", "reprovado", "cancelado", "concluido"}


def sanitize_comment(comment: str | None) -> str | None:
    if not comment:
        return comment
    sanitized = re.sub(r"\b\d{11}\b", "[CPF_MASKED]", comment)
    sanitized = re.sub(r"R\$\s?\d[\d\.,]*", "R$ [MASKED]", sanitized)
    return sanitized[:2000]


def _find_responsavel_for_etapa(db: Session, etapa: WorkflowEtapa, explicit_user_id: int | None = None) -> int | None:
    if explicit_user_id is not None:
        return explicit_user_id
    if etapa.perfil_responsavel:
        usuario = db.scalar(select(Usuario).where(Usuario.perfil == etapa.perfil_responsavel, Usuario.ativo.is_(True)).order_by(Usuario.id.asc()))
        if usuario is not None:
            return usuario.id
    return None


def ensure_default_workflow(db: Session, modulo: str, usuario_id: int | None = None):
    workflow = crud_workflows.buscar_workflow_por_modulo(db, modulo)
    if workflow is not None:
        return workflow
    workflow = crud_workflows.criar_workflow(
        db,
        {"nome": f"workflow_{modulo}", "modulo": modulo, "descricao": f"Workflow padrao do modulo {modulo}", "ativo": True},
        usuario_id,
    )
    crud_workflows.criar_etapa(
        db,
        workflow.id,
        {
            "nome": "Aprovacao inicial",
            "ordem": 1,
            "perfil_responsavel": "dp",
            "permissao_requerida": f"{modulo}:update" if modulo not in {"ponto", "folha"} else ("ponto:approve" if modulo == "ponto" else "folha:update"),
            "obrigatoria": True,
            "prazo_horas": 48,
            "permite_reprovar": True,
            "permite_devolver": True,
            "ativo": True,
        },
        usuario_id,
    )
    return workflow


def request_approval_for_entity(
    db: Session,
    *,
    modulo: str,
    entidade_tipo: str,
    entidade_id: int,
    solicitante_id: int | None = None,
    responsavel_id: int | None = None,
    comentario: str | None = None,
) -> object:
    existente = crud_workflows.buscar_instancia_por_entidade(db, entidade_tipo, entidade_id)
    if existente is not None and existente.status not in FINAL_STATUSES:
        return existente
    workflow = ensure_default_workflow(db, modulo, solicitante_id)
    etapa = crud_workflows.listar_etapas(db, workflow.id)[0]
    instancia = crud_workflows.criar_instancia(
        db,
        {
            "workflow_id": workflow.id,
            "entidade_tipo": entidade_tipo,
            "entidade_id": entidade_id,
            "status": "aguardando_aprovacao",
            "etapa_atual_id": etapa.id,
            "solicitante_id": solicitante_id,
            "responsavel_atual_id": _find_responsavel_for_etapa(db, etapa, responsavel_id),
        },
        solicitante_id,
    )
    crud_workflows.registrar_historico(
        db,
        {
            "instancia_id": instancia.id,
            "etapa_id": etapa.id,
            "usuario_id": solicitante_id,
            "acao": "enviou",
            "comentario": sanitize_comment(comentario),
        },
    )
    log_action(db, tabela="workflow_instancias", acao="solicitar_aprovacao", registro_id=instancia.id, usuario_id=solicitante_id, origem="workflow")
    if instancia.responsavel_atual_id:
        notify_user(
            db,
            usuario_id=instancia.responsavel_atual_id,
            titulo="Aprovacao pendente",
            mensagem=f"Existe uma aprovacao pendente para {entidade_tipo} #{entidade_id}.",
            tipo="aprovacao_pendente",
            severidade="media",
            link_entidade_tipo=entidade_tipo,
            link_entidade_id=entidade_id,
            origem="workflow",
        )
    return instancia


def approve_instance(db: Session, instancia_id: int, usuario_id: int, comentario: str | None = None):
    instancia = crud_workflows.buscar_instancia(db, instancia_id)
    if instancia is None:
        raise ValueError("Instancia de workflow nao encontrada.")
    if instancia.status in FINAL_STATUSES:
        raise ValueError("Workflow concluido nao pode ser alterado sem reabertura controlada.")
    workflow = crud_workflows.buscar_workflow(db, instancia.workflow_id)
    etapas = crud_workflows.listar_etapas(db, workflow.id)
    etapa_atual = next((item for item in etapas if item.id == instancia.etapa_atual_id), None)
    if etapa_atual and etapa_atual.permissao_requerida:
        usuario = db.get(Usuario, usuario_id)
        if usuario is None or not has_permission(usuario.perfil, etapa_atual.permissao_requerida):
            raise ValueError("Usuario sem permissao para aprovar esta etapa.")
    current_index = next((idx for idx, item in enumerate(etapas) if item.id == instancia.etapa_atual_id), 0)
    prox_etapa = etapas[current_index + 1] if current_index + 1 < len(etapas) else None
    payload = {"status": "concluido" if prox_etapa is None else "aguardando_aprovacao", "etapa_atual_id": None if prox_etapa is None else prox_etapa.id}
    if prox_etapa is None:
        payload["concluido_em"] = datetime.now(UTC).replace(tzinfo=None)
        payload["responsavel_atual_id"] = None
    else:
        payload["responsavel_atual_id"] = _find_responsavel_for_etapa(db, prox_etapa)
    instancia = crud_workflows.atualizar_instancia(db, instancia, payload, usuario_id)
    crud_workflows.registrar_historico(db, {"instancia_id": instancia.id, "etapa_id": etapa_atual.id if etapa_atual else None, "usuario_id": usuario_id, "acao": "aprovou", "comentario": sanitize_comment(comentario)})
    log_action(db, tabela="workflow_instancias", acao="aprovar_workflow", registro_id=instancia.id, usuario_id=usuario_id, origem="workflow")
    if instancia.solicitante_id:
        notify_user(db, usuario_id=instancia.solicitante_id, titulo="Aprovacao concluida", mensagem=f"O workflow de {instancia.entidade_tipo} #{instancia.entidade_id} foi aprovado.", tipo="aprovacao_concluida", severidade="info", link_entidade_tipo=instancia.entidade_tipo, link_entidade_id=instancia.entidade_id, origem="workflow")
    if instancia.responsavel_atual_id:
        notify_user(db, usuario_id=instancia.responsavel_atual_id, titulo="Aprovacao pendente", mensagem=f"Nova etapa pendente para {instancia.entidade_tipo} #{instancia.entidade_id}.", tipo="aprovacao_pendente", severidade="media", link_entidade_tipo=instancia.entidade_tipo, link_entidade_id=instancia.entidade_id, origem="workflow")
    return instancia


def reject_instance(db: Session, instancia_id: int, usuario_id: int, comentario: str):
    if not comentario:
        raise ValueError("Reprovacao exige comentario.")
    instancia = crud_workflows.buscar_instancia(db, instancia_id)
    if instancia is None:
        raise ValueError("Instancia de workflow nao encontrada.")
    instancia = crud_workflows.atualizar_instancia(db, instancia, {"status": "reprovado", "concluido_em": datetime.now(UTC).replace(tzinfo=None)}, usuario_id)
    crud_workflows.registrar_historico(db, {"instancia_id": instancia.id, "etapa_id": instancia.etapa_atual_id, "usuario_id": usuario_id, "acao": "reprovou", "comentario": sanitize_comment(comentario)})
    log_action(db, tabela="workflow_instancias", acao="reprovar_workflow", registro_id=instancia.id, usuario_id=usuario_id, origem="workflow")
    if instancia.solicitante_id:
        notify_user(db, usuario_id=instancia.solicitante_id, titulo="Aprovacao reprovada", mensagem=f"O workflow de {instancia.entidade_tipo} #{instancia.entidade_id} foi reprovado.", tipo="aprovacao_concluida", severidade="alta", link_entidade_tipo=instancia.entidade_tipo, link_entidade_id=instancia.entidade_id, origem="workflow")
    return instancia


def return_instance(db: Session, instancia_id: int, usuario_id: int, comentario: str):
    if not comentario:
        raise ValueError("Devolucao exige comentario.")
    instancia = crud_workflows.buscar_instancia(db, instancia_id)
    if instancia is None:
        raise ValueError("Instancia de workflow nao encontrada.")
    instancia = crud_workflows.atualizar_instancia(db, instancia, {"status": "devolvido"}, usuario_id)
    crud_workflows.registrar_historico(db, {"instancia_id": instancia.id, "etapa_id": instancia.etapa_atual_id, "usuario_id": usuario_id, "acao": "devolveu", "comentario": sanitize_comment(comentario)})
    log_action(db, tabela="workflow_instancias", acao="devolver_workflow", registro_id=instancia.id, usuario_id=usuario_id, origem="workflow")
    if instancia.solicitante_id:
        notify_user(db, usuario_id=instancia.solicitante_id, titulo="Aprovacao devolvida", mensagem=f"O workflow de {instancia.entidade_tipo} #{instancia.entidade_id} foi devolvido para ajuste.", tipo="aprovacao_concluida", severidade="media", link_entidade_tipo=instancia.entidade_tipo, link_entidade_id=instancia.entidade_id, origem="workflow")
    return instancia


def cancel_instance(db: Session, instancia_id: int, usuario_id: int, comentario: str | None = None):
    instancia = crud_workflows.buscar_instancia(db, instancia_id)
    if instancia is None:
        raise ValueError("Instancia de workflow nao encontrada.")
    instancia = crud_workflows.atualizar_instancia(db, instancia, {"status": "cancelado", "cancelado_em": datetime.now(UTC).replace(tzinfo=None)}, usuario_id)
    crud_workflows.registrar_historico(db, {"instancia_id": instancia.id, "etapa_id": instancia.etapa_atual_id, "usuario_id": usuario_id, "acao": "cancelou", "comentario": sanitize_comment(comentario)})
    log_action(db, tabela="workflow_instancias", acao="cancelar_workflow", registro_id=instancia.id, usuario_id=usuario_id, origem="workflow")
    return instancia


def reassign_instance(db: Session, instancia_id: int, responsavel_id: int, usuario_id: int, comentario: str | None = None):
    instancia = crud_workflows.buscar_instancia(db, instancia_id)
    if instancia is None:
        raise ValueError("Instancia de workflow nao encontrada.")
    instancia = crud_workflows.atualizar_instancia(db, instancia, {"responsavel_atual_id": responsavel_id}, usuario_id)
    crud_workflows.registrar_historico(db, {"instancia_id": instancia.id, "etapa_id": instancia.etapa_atual_id, "usuario_id": usuario_id, "acao": "alterou_responsavel", "comentario": sanitize_comment(comentario)})
    log_action(db, tabela="workflow_instancias", acao="alterar_responsavel_workflow", registro_id=instancia.id, usuario_id=usuario_id, origem="workflow")
    notify_user(db, usuario_id=responsavel_id, titulo="Aprovacao atribuida", mensagem=f"Voce recebeu a aprovacao de {instancia.entidade_tipo} #{instancia.entidade_id}.", tipo="aprovacao_pendente", severidade="media", link_entidade_tipo=instancia.entidade_tipo, link_entidade_id=instancia.entidade_id, origem="workflow")
    return instancia
