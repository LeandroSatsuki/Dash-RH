from datetime import date, timedelta

from src.crud import colaboradores as crud_colaboradores
from src.crud import ferias as crud_ferias
from src.services.data_quality import generate_operational_quality_report


def test_data_quality_detecta_problemas(db):
    col = crud_colaboradores.criar(
        db,
        {"nome_completo": "Sem Departamento", "cpf": "123", "regime_contratual": "CLT", "status": "ativo"},
        1,
    )
    crud_ferias.criar(
        db,
        {"colaborador_id": col.id, "data_inicio": date.today(), "data_fim": date.today(), "data_limite_gozo": date.today() - timedelta(days=1), "status": "planejada"},
        1,
    )
    issues = generate_operational_quality_report(db)
    tipos = {item["tipo"] for item in issues}
    assert "CPF inválido" in tipos or "CPF ausente para CLT" in tipos
    assert "Departamento ausente" in tipos
    assert "Férias vencidas" in tipos
