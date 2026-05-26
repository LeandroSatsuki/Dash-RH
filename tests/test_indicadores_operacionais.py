from datetime import date

from src.crud import colaboradores as crud_colaboradores
from src.crud import folha as crud_folha
from src.services.indicadores import indicadores_operacionais


def test_indicadores_operacionais_basicos(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Indicador Fake", "cpf": "90000000007", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000, "data_admissao": date(2026, 1, 1)}, 1)
    dados = indicadores_operacionais(db, ano=2026, mes=1)
    assert "kpis" in dados
    assert dados["kpis"]["colaboradores_ativos"] >= 1


def test_indicadores_operacionais_com_folha(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Indicador Folha", "cpf": "90000000008", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)
    rubrica = crud_folha.criar_rubrica(db, {"codigo": "SAL2", "descricao": "Salario", "tipo": "provento"}, 1)
    competencia = crud_folha.criar_competencia(db, {"ano": 2026, "mes": 1, "competencia": "2026-01", "status": "aberta"}, 1)
    crud_folha.criar_lancamento(db, {"competencia_id": competencia.id, "colaborador_id": colaborador.id, "rubrica_id": rubrica.id, "tipo": "provento", "valor": "1000,00"}, 1)
    dados = indicadores_operacionais(db, ano=2026, mes=1)
    assert dados["kpis"]["folha_bruta"] >= 1000.0
