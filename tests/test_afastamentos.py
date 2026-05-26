from datetime import date

from src.crud import afastamentos as crud_afastamentos
from src.crud import colaboradores as crud_colaboradores


def test_afastamento_com_datas_invalidas_bloqueado(db):
    colaborador = crud_colaboradores.criar(
        db,
        {"nome_completo": "Afastado", "cpf": "12345678901", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1200},
        1,
    )
    try:
        crud_afastamentos.criar(
            db,
            {"colaborador_id": colaborador.id, "tipo": "atestado_medico", "data_inicio": date(2026, 5, 10), "data_fim": date(2026, 5, 1)},
            1,
        )
        assert False, "Era esperado erro"
    except ValueError as exc:
        assert "Afastamento" in str(exc)
