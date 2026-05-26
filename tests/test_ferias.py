from datetime import date

from src.crud import colaboradores as crud_colaboradores
from src.crud import ferias as crud_ferias


def test_ferias_com_datas_invalidas_bloqueadas(db):
    colaborador = crud_colaboradores.criar(
        db,
        {"nome_completo": "Férias", "cpf": "12345678901", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1200},
        1,
    )
    try:
        crud_ferias.criar(
            db,
            {"colaborador_id": colaborador.id, "data_inicio": date(2026, 5, 10), "data_fim": date(2026, 5, 1), "status": "planejada"},
            1,
        )
        assert False, "Era esperado erro"
    except ValueError as exc:
        assert "Férias" in str(exc)
