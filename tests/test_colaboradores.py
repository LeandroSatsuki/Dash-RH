from src.crud import auditoria as crud_auditoria
from src.crud import colaboradores as crud_colaboradores


def test_criacao_colaborador(db):
    colaborador = crud_colaboradores.criar(
        db,
        {"nome_completo": "Maria Silva", "cpf": "12345678901", "regime_contratual": "CLT", "status": "ativo", "salario_base": 2500.0},
        1,
    )
    assert colaborador.id is not None
    assert colaborador.nome_completo == "Maria Silva"


def test_cpf_obrigatorio_para_clt(db):
    try:
        crud_colaboradores.criar(db, {"nome_completo": "Sem CPF", "regime_contratual": "CLT", "status": "ativo"}, 1)
        assert False, "Era esperado erro de validação"
    except ValueError as exc:
        assert "CPF" in str(exc)


def test_salario_negativo_bloqueado(db):
    try:
        crud_colaboradores.criar(
            db,
            {"nome_completo": "Salário Negativo", "cpf": "12345678901", "regime_contratual": "CLT", "status": "ativo", "salario_base": -10},
            1,
        )
        assert False, "Era esperado erro de validação"
    except ValueError as exc:
        assert "Salário" in str(exc)


def test_soft_delete_e_auditoria(db):
    colaborador = crud_colaboradores.criar(
        db,
        {"nome_completo": "João", "cpf": "12345678901", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000},
        1,
    )
    crud_colaboradores.remover(db, colaborador.id, 1)
    assert colaborador.deletado_em is not None
    logs = crud_auditoria.listar(db)
    assert any(log.tabela == "colaboradores" and log.acao in {"create", "soft_delete"} for log in logs)
