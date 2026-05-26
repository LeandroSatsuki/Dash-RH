from datetime import date

from src.crud import beneficios as crud_beneficios
from src.crud import colaboradores as crud_colaboradores
from src.crud import desligamentos as crud_desligamentos
from src.services.audit_service import list_audit_logs
from src.services.historico import listar_historico_colaborador


def _colaborador(db):
    return crud_colaboradores.criar(db, {"nome_completo": "Desligamento Fake", "cpf": "90000000006", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000, "data_admissao": date(2025, 1, 1)}, 1)


def test_cria_desligamento(db):
    colaborador = _colaborador(db)
    desligamento = crud_desligamentos.criar(db, {"colaborador_id": colaborador.id, "data_desligamento": date(2026, 5, 1), "tipo_rescisao": "pedido_demissao"}, 1)
    assert desligamento.id is not None


def test_bloqueia_conclusao_sem_tipo(db):
    colaborador = _colaborador(db)
    desligamento = crud_desligamentos.criar(db, {"colaborador_id": colaborador.id, "data_desligamento": date(2026, 5, 1), "tipo_rescisao": None}, 1)
    try:
        crud_desligamentos.concluir(db, desligamento.id, 1)
        assert False, "Era esperado bloqueio"
    except ValueError as exc:
        assert "rescisao" in str(exc)


def test_conclusao_desliga_colaborador_e_beneficio(db):
    colaborador = _colaborador(db)
    beneficio = crud_beneficios.criar(db, {"nome": "vale_refeicao", "tipo": "beneficio", "status": "ativo"}, 1)
    vinculo = crud_beneficios.vincular_ao_colaborador(db, {"colaborador_id": colaborador.id, "beneficio_id": beneficio.id, "valor_empresa": "100,00", "data_inicio": date(2026, 1, 1), "status": "ativo"}, 1)
    desligamento = crud_desligamentos.criar(db, {"colaborador_id": colaborador.id, "data_desligamento": date(2026, 5, 1), "tipo_rescisao": "pedido_demissao"}, 1)
    crud_desligamentos.concluir(db, desligamento.id, 1)
    atualizado = crud_colaboradores.buscar_por_id(db, colaborador.id)
    historico = listar_historico_colaborador(db, colaborador.id)
    vinculos = crud_beneficios.listar_vinculos(db)
    assert atualizado.status == "desligado"
    assert any(item.tipo_evento == "desligamento" for item in historico)
    assert any(item.id == vinculo.id and item.status == "encerrado" for item in vinculos)


def test_cancelamento_gera_auditoria(db):
    colaborador = _colaborador(db)
    desligamento = crud_desligamentos.criar(db, {"colaborador_id": colaborador.id, "data_desligamento": date(2026, 5, 1), "tipo_rescisao": "pedido_demissao"}, 1)
    crud_desligamentos.cancelar(db, desligamento.id, 1)
    logs = list_audit_logs(db, tabela="desligamentos", acao="cancelar_desligamento")
    assert len(logs) == 1
