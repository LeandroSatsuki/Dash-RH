from src.crud import colaboradores as crud_colaboradores
from src.crud import folha as crud_folha
from src.services.audit_service import list_audit_logs


def _setup_folha(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Folha Fake", "cpf": "90000000005", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)
    rubrica = crud_folha.criar_rubrica(db, {"codigo": "SAL", "descricao": "Salario", "tipo": "provento"}, 1)
    competencia = crud_folha.criar_competencia(db, {"ano": 2026, "mes": 8, "competencia": "2026-08", "status": "aberta"}, 1)
    return colaborador, rubrica, competencia


def test_resumo_competencia(db):
    colaborador, rubrica, competencia = _setup_folha(db)
    crud_folha.criar_lancamento(db, {"competencia_id": competencia.id, "colaborador_id": colaborador.id, "rubrica_id": rubrica.id, "tipo": "provento", "valor": "1500,00"}, 1)
    resumo = crud_folha.resumo_competencia(db, competencia.id)
    assert resumo["total_proventos"] == 1500.0


def test_exportacao_competencia(db):
    colaborador, rubrica, competencia = _setup_folha(db)
    crud_folha.criar_lancamento(db, {"competencia_id": competencia.id, "colaborador_id": colaborador.id, "rubrica_id": rubrica.id, "tipo": "provento", "valor": "1500,00"}, 1)
    export = crud_folha.exportar_competencia(db, competencia.id)
    assert export[0]["rubrica_codigo"] == "SAL"


def test_fechada_bloqueia_edicao(db):
    colaborador, rubrica, competencia = _setup_folha(db)
    lanc = crud_folha.criar_lancamento(db, {"competencia_id": competencia.id, "colaborador_id": colaborador.id, "rubrica_id": rubrica.id, "tipo": "provento", "valor": "1500,00"}, 1)
    crud_folha.fechar_competencia(db, competencia.id, 1)
    try:
        crud_folha.editar_lancamento(db, lanc.id, {"valor": "1200,00"}, 1)
        assert False, "Era esperado bloqueio"
    except ValueError as exc:
        assert "fechada" in str(exc)


def test_reabertura_gera_auditoria(db):
    _, _, competencia = _setup_folha(db)
    crud_folha.fechar_competencia(db, competencia.id, 1)
    crud_folha.reabrir_competencia(db, competencia.id, 1)
    logs = list_audit_logs(db, tabela="competencias_folha", acao="reabrir_competencia")
    assert len(logs) == 1
