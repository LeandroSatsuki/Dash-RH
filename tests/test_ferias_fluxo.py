from datetime import date

from src.crud import colaboradores as crud_colaboradores
from src.crud import ferias as crud_ferias
from src.services.audit_service import list_audit_logs
from src.services.historico import listar_historico_colaborador


def _colaborador(db, status="ativo"):
    payload = {"nome_completo": "Ferias Fake", "cpf": "90000000002", "regime_contratual": "CLT", "status": status, "salario_base": 1000}
    if status == "desligado":
        payload["data_desligamento"] = date(2026, 2, 1)
    return crud_colaboradores.criar(db, payload, 1)


def test_aprova_ferias(db):
    colaborador = _colaborador(db)
    ferias = crud_ferias.criar(db, {"colaborador_id": colaborador.id, "data_inicio": date(2026, 2, 1), "data_fim": date(2026, 2, 10), "dias_direito": 30, "dias_gozados": 10, "dias_restantes": 20}, 1)
    aprovadas = crud_ferias.aprovar(db, ferias.id, 1)
    assert aprovadas.status == "aprovada"


def test_bloqueia_sobreposicao(db):
    colaborador = _colaborador(db)
    crud_ferias.criar(db, {"colaborador_id": colaborador.id, "data_inicio": date(2026, 2, 1), "data_fim": date(2026, 2, 10), "dias_direito": 30, "dias_gozados": 10, "dias_restantes": 20, "status": "aprovada"}, 1)
    ferias = crud_ferias.criar(db, {"colaborador_id": colaborador.id, "data_inicio": date(2026, 2, 5), "data_fim": date(2026, 2, 15), "dias_direito": 30, "dias_gozados": 10, "dias_restantes": 20}, 1)
    try:
        crud_ferias.aprovar(db, ferias.id, 1)
        assert False, "Era esperado bloqueio"
    except ValueError as exc:
        assert "sobrepostas" in str(exc)


def test_bloqueia_aprovacao_para_desligado(db):
    colaborador = _colaborador(db, status="desligado")
    ferias = crud_ferias.criar(db, {"colaborador_id": colaborador.id, "data_inicio": date(2026, 2, 1), "data_fim": date(2026, 2, 10), "dias_direito": 30, "dias_gozados": 10, "dias_restantes": 20}, 1)
    try:
        crud_ferias.aprovar(db, ferias.id, 1)
        assert False, "Era esperado bloqueio"
    except ValueError as exc:
        assert "desligado" in str(exc)


def test_conclusao_cria_historico_e_auditoria(db):
    colaborador = _colaborador(db)
    ferias = crud_ferias.criar(db, {"colaborador_id": colaborador.id, "data_inicio": date(2026, 2, 1), "data_fim": date(2026, 2, 10), "dias_direito": 30, "dias_gozados": 10, "dias_restantes": 20}, 1)
    crud_ferias.concluir(db, ferias.id, 1)
    historico = listar_historico_colaborador(db, colaborador.id)
    logs = list_audit_logs(db, tabela="ferias", acao="concluir_ferias")
    assert any(item.tipo_evento == "ferias" for item in historico)
    assert len(logs) == 1
