from datetime import UTC, datetime, timedelta

from src.crud import tarefas as crud_tarefas
from src.services import task_service


def test_tarefa_critica_exige_prazo(db):
    try:
        task_service.create_task(db, {"titulo": "Critica", "modulo": "geral", "prioridade": "critica", "responsavel_id": 1}, 1)
        assert False, "Era esperado prazo obrigatorio."
    except ValueError as exc:
        assert "prazo" in str(exc).lower()


def test_tarefa_concluida_recebe_data(db):
    tarefa = task_service.create_task(db, {"titulo": "Concluir", "modulo": "geral", "responsavel_id": 1, "prazo": datetime.now(UTC).replace(tzinfo=None)}, 1)
    tarefa = task_service.complete_task(db, tarefa.id, 1)
    assert tarefa.concluido_em is not None


def test_tarefa_cancelada_exige_motivo(db):
    tarefa = task_service.create_task(db, {"titulo": "Cancelar", "modulo": "geral", "responsavel_id": 1, "prazo": datetime.now(UTC).replace(tzinfo=None)}, 1)
    try:
        task_service.cancel_task(db, tarefa.id, "", 1)
        assert False, "Era esperado motivo obrigatorio."
    except ValueError as exc:
        assert "motivo" in str(exc).lower()


def test_tarefa_comentario_sanitiza_cpf(db):
    tarefa = task_service.create_task(db, {"titulo": "Comentada", "modulo": "geral", "responsavel_id": 1, "prazo": datetime.now(UTC).replace(tzinfo=None)}, 1)
    comentario = task_service.comment_task(db, tarefa.id, "cpf 12345678901", 1)
    assert "[CPF_MASKED]" in comentario.comentario
