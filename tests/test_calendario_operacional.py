from datetime import date, timedelta

from src.crud import colaboradores as crud_colaboradores
from src.crud import ferias as crud_ferias
from src.services.calendar_service import build_calendar_events


def test_calendario_retorna_eventos(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Calendario", "cpf": "90000000057", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)
    crud_ferias.criar(db, {"colaborador_id": colaborador.id, "data_inicio": date.today(), "data_fim": date.today() + timedelta(days=5), "status": "planejada"}, 1)
    eventos = build_calendar_events(db)
    assert any(item["tipo"] == "ferias" for item in eventos)
