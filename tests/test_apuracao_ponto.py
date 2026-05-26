from datetime import date, timedelta

from src.crud import afastamentos as crud_afastamentos
from src.crud import colaboradores as crud_colaboradores
from src.crud import ferias as crud_ferias
from src.crud import jornadas as crud_jornadas
from src.crud import ponto as crud_ponto


def _setup_base(db, status="ativo"):
    colaborador = crud_colaboradores.criar(
        db,
        {"nome_completo": f"Apuracao {status}", "cpf": f"9000000004{1 if status == 'ativo' else 2}", "regime_contratual": "CLT", "status": status, "salario_base": 2000},
        1,
    )
    jornada = crud_jornadas.criar_jornada(db, {"nome": f"Jornada {status}", "tolerancia_entrada_minutos": 5, "tolerancia_saida_minutos": 5}, 1)
    crud_jornadas.criar_turno(
        db,
        jornada.id,
        {"dia_semana": date.today().weekday(), "hora_entrada": "08:00", "hora_saida_intervalo": "12:00", "hora_retorno_intervalo": "13:00", "hora_saida": "17:00"},
        1,
    )
    crud_jornadas.vincular_jornada_colaborador(db, colaborador.id, {"jornada_id": jornada.id, "data_inicio": date.today() - timedelta(days=1)}, 1)
    return colaborador


def test_apuracao_calcula_horas_extras(db):
    colaborador = _setup_base(db)
    for tipo, horario in [("entrada", "08:00"), ("saida_intervalo", "12:00"), ("retorno_intervalo", "13:00"), ("saida", "18:30")]:
        crud_ponto.criar_marcacao(db, {"colaborador_id": colaborador.id, "data": date.today(), "tipo": tipo, "horario": horario, "origem": "manual"}, 1)
    apuracoes = crud_ponto.apurar_periodo(db, data_inicio=date.today(), data_fim=date.today(), usuario_id=1)
    assert float(apuracoes[0].horas_extras or 0) > 0


def test_apuracao_marca_inconsistente_sem_marcacoes(db):
    colaborador = _setup_base(db)
    apuracoes = crud_ponto.apurar_periodo(db, data_inicio=date.today(), data_fim=date.today(), usuario_id=1)
    assert apuracoes[0].status == "inconsistente"
    assert apuracoes[0].falta is True


def test_apuracao_nao_exige_marcacao_em_ferias(db):
    colaborador = _setup_base(db)
    crud_ferias.criar(
        db,
        {"colaborador_id": colaborador.id, "data_inicio": date.today(), "data_fim": date.today(), "status": "aprovada"},
        1,
    )
    apuracoes = crud_ponto.apurar_periodo(db, data_inicio=date.today(), data_fim=date.today(), usuario_id=1)
    assert apuracoes[0].status == "aprovado"
