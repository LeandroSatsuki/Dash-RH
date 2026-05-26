from datetime import date, timedelta

from src.crud import colaboradores as crud_colaboradores
from src.crud import documentos_obrigatorios as crud_docs
from src.crud import sst as crud_sst
from src.services.scheduler_rules import run_daily_checks


def test_daily_checks_cria_tarefas(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Daily", "cpf": "90000000055", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)
    tipo = crud_docs.criar_tipo_documento(db, {"nome": "doc_daily", "ativo": True}, 1)
    crud_docs.criar_regra(db, {"tipo_documento_id": tipo.id, "regime_contratual": "CLT", "obrigatorio": True}, 1)
    crud_docs.gerar_pendencias(db, 1)
    result = run_daily_checks(db)
    assert result["tarefas_processadas"] > 0


def test_daily_checks_e_idempotente_no_mesmo_dia(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Daily 2", "cpf": "90000000056", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)
    tipo = crud_docs.criar_tipo_documento(db, {"nome": "doc_daily_2", "ativo": True}, 1)
    crud_docs.criar_regra(db, {"tipo_documento_id": tipo.id, "regime_contratual": "CLT", "obrigatorio": True}, 1)
    crud_docs.gerar_pendencias(db, 1)
    run_daily_checks(db)
    first = run_daily_checks(db)
    second = run_daily_checks(db)
    assert first["tarefas_processadas"] >= second["tarefas_processadas"]
