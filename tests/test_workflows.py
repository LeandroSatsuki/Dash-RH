from src.crud import workflows as crud_workflows
from src.services import workflow_service
from src.services.audit_service import list_audit_logs


def test_workflow_default_cria_etapa(db):
    workflow = workflow_service.ensure_default_workflow(db, "ferias", 1)
    etapas = crud_workflows.listar_etapas(db, workflow.id)
    assert workflow.modulo == "ferias"
    assert len(etapas) == 1


def test_workflow_reprovacao_exige_comentario(db):
    instancia = workflow_service.request_approval_for_entity(db, modulo="ferias", entidade_tipo="ferias", entidade_id=10, solicitante_id=1)
    try:
        workflow_service.reject_instance(db, instancia.id, 1, "")
        assert False, "Era esperado comentario obrigatorio."
    except ValueError as exc:
        assert "comentario" in str(exc).lower()


def test_workflow_aprovacao_registra_auditoria(db):
    instancia = workflow_service.request_approval_for_entity(db, modulo="ferias", entidade_tipo="ferias", entidade_id=11, solicitante_id=1)
    workflow_service.approve_instance(db, instancia.id, 1, "ok")
    logs = list_audit_logs(db, tabela="workflow_instancias", acao="aprovar_workflow")
    assert len(logs) == 1
