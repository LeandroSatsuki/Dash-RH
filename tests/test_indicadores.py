from src.services.indicadores import absenteismo, turnover


def test_turnover_nao_quebra_com_divisao_por_zero():
    assert turnover(2, 2, 0) == 0.0


def test_absenteismo_nao_quebra_com_divisao_por_zero():
    assert absenteismo(10, 0) == 0.0
