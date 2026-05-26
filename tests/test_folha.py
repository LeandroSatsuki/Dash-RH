from src.crud import colaboradores as crud_colaboradores
from src.crud import folha as crud_folha


def test_competencia_fechada_bloqueia_lancamento(db):
    colaborador = crud_colaboradores.criar(
        db,
        {"nome_completo": "Folha", "cpf": "12345678901", "regime_contratual": "CLT", "status": "ativo", "salario_base": 2000},
        1,
    )
    rubrica = crud_folha.criar_rubrica(db, {"codigo": "100", "descricao": "Salário", "tipo": "provento"}, 1)
    competencia = crud_folha.criar_competencia(db, {"ano": 2026, "mes": 5, "competencia": "2026-05", "status": "aberta"}, 1)
    crud_folha.fechar_competencia(db, competencia.id, 1)
    try:
        crud_folha.criar_lancamento(
            db,
            {"competencia_id": competencia.id, "colaborador_id": colaborador.id, "rubrica_id": rubrica.id, "tipo": "provento", "valor": 1000},
            1,
        )
        assert False, "Era esperado bloqueio"
    except ValueError as exc:
        assert "Competência fechada" in str(exc)
