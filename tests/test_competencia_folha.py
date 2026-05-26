from src.crud import colaboradores as crud_colaboradores
from src.crud import folha as crud_folha


def test_nao_permite_duas_competencias_abertas(db):
    crud_folha.criar_competencia(db, {"ano": 2026, "mes": 6, "competencia": "2026-06", "status": "aberta"}, 1)
    try:
        crud_folha.criar_competencia(db, {"ano": 2026, "mes": 6, "competencia": "2026-06", "status": "aberta"}, 1)
        assert False, "Era esperado bloqueio"
    except ValueError as exc:
        assert "duas competências" in str(exc)


def test_fechamento_cria_snapshot(db):
    colaborador = crud_colaboradores.criar(
        db,
        {"nome_completo": "Comp", "cpf": "12345678901", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000},
        1,
    )
    rubrica = crud_folha.criar_rubrica(db, {"codigo": "R1", "descricao": "Provento", "tipo": "provento"}, 1)
    competencia = crud_folha.criar_competencia(db, {"ano": 2026, "mes": 7, "competencia": "2026-07", "status": "aberta"}, 1)
    crud_folha.criar_lancamento(db, {"competencia_id": competencia.id, "colaborador_id": colaborador.id, "rubrica_id": rubrica.id, "tipo": "provento", "valor": 1000}, 1)
    crud_folha.fechar_competencia(db, competencia.id, 1)
    snapshot = crud_folha.buscar_snapshot(db, competencia.id)
    assert snapshot is not None
    assert float(snapshot.total_proventos) == 1000.0
