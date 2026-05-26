from datetime import date

from src.crud import beneficios as crud_beneficios
from src.crud import colaboradores as crud_colaboradores
from src.services.audit_service import list_audit_logs


def _colaborador(db, status="ativo"):
    payload = {"nome_completo": "Beneficio Fake", "cpf": "90000000004", "regime_contratual": "CLT", "status": status, "salario_base": 1000}
    if status == "desligado":
        payload["data_desligamento"] = date(2026, 4, 1)
    return crud_colaboradores.criar(db, payload, 1)


def _beneficio(db):
    return crud_beneficios.criar(db, {"nome": "vale_refeicao", "tipo": "beneficio", "status": "ativo"}, 1)


def test_vincula_beneficio(db):
    colaborador = _colaborador(db)
    beneficio = _beneficio(db)
    vinculo = crud_beneficios.vincular_ao_colaborador(db, {"colaborador_id": colaborador.id, "beneficio_id": beneficio.id, "valor_empresa": "200,00", "valor_colaborador": "20,00", "data_inicio": date(2026, 4, 1), "status": "ativo"}, 1)
    assert vinculo.id is not None


def test_bloqueia_valor_negativo(db):
    colaborador = _colaborador(db)
    beneficio = _beneficio(db)
    try:
        crud_beneficios.vincular_ao_colaborador(db, {"colaborador_id": colaborador.id, "beneficio_id": beneficio.id, "valor_empresa": "-1,00", "data_inicio": date(2026, 4, 1), "status": "ativo"}, 1)
        assert False, "Era esperado bloqueio"
    except ValueError as exc:
        assert "negativo" in str(exc)


def test_bloqueia_beneficio_ativo_para_desligado(db):
    colaborador = _colaborador(db, status="desligado")
    beneficio = _beneficio(db)
    try:
        crud_beneficios.vincular_ao_colaborador(db, {"colaborador_id": colaborador.id, "beneficio_id": beneficio.id, "valor_empresa": "200,00", "data_inicio": date(2026, 4, 1), "status": "ativo"}, 1)
        assert False, "Era esperado bloqueio"
    except ValueError as exc:
        assert "desligado" in str(exc)


def test_encerrar_vinculo_gera_auditoria(db):
    colaborador = _colaborador(db)
    beneficio = _beneficio(db)
    vinculo = crud_beneficios.vincular_ao_colaborador(db, {"colaborador_id": colaborador.id, "beneficio_id": beneficio.id, "valor_empresa": "200,00", "valor_colaborador": "20,00", "data_inicio": date(2026, 4, 1), "status": "ativo"}, 1)
    crud_beneficios.encerrar_vinculo(db, vinculo.id, 1)
    logs = list_audit_logs(db, tabela="colaborador_beneficios", acao="encerrar_beneficio")
    assert len(logs) == 1
