from datetime import date

from src.crud import banco_horas as crud_banco_horas
from src.crud import colaboradores as crud_colaboradores


def _colaborador(db):
    return crud_colaboradores.criar(
        db,
        {"nome_completo": "Banco Horas", "cpf": "90000000034", "regime_contratual": "CLT", "status": "ativo", "salario_base": 2000},
        1,
    )


def test_credito_e_debito_atualizam_saldo(db):
    colaborador = _colaborador(db)
    crud_banco_horas.criar_movimento(db, {"colaborador_id": colaborador.id, "data": date.today(), "origem": "ajuste_manual", "tipo": "credito", "horas": "2,00", "descricao": "Credito"}, 1)
    crud_banco_horas.criar_movimento(db, {"colaborador_id": colaborador.id, "data": date.today(), "origem": "ajuste_manual", "tipo": "debito", "horas": "1,00", "descricao": "Debito"}, 1)
    assert float(crud_banco_horas.saldo_colaborador(db, colaborador.id)) == 1.0


def test_ajuste_exige_motivo(db):
    colaborador = _colaborador(db)
    try:
        crud_banco_horas.criar_movimento(db, {"colaborador_id": colaborador.id, "data": date.today(), "origem": "ajuste_manual", "tipo": "ajuste", "horas": "1,00"}, 1)
        assert False, "Esperava exigencia de motivo."
    except ValueError as exc:
        assert "motivo" in str(exc)


def test_config_bloqueia_saldo_negativo(db):
    colaborador = _colaborador(db)
    crud_banco_horas.set_config(db, "permitir_banco_horas_negativo", "false", usuario_id=1)
    try:
        crud_banco_horas.criar_movimento(db, {"colaborador_id": colaborador.id, "data": date.today(), "origem": "ajuste_manual", "tipo": "debito", "horas": "1,00", "descricao": "Debito"}, 1)
        assert False, "Esperava bloqueio de saldo negativo."
    except ValueError as exc:
        assert "negativo" in str(exc)
