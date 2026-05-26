from datetime import date, timedelta

from src.crud import colaboradores as crud_colaboradores
from src.crud import jornadas as crud_jornadas
from src.crud import ponto as crud_ponto
from src.services.audit_service import list_audit_logs


def _setup_colaborador_com_jornada(db):
    colaborador = crud_colaboradores.criar(
        db,
        {"nome_completo": "Ponto Demo", "cpf": "90000000032", "regime_contratual": "CLT", "status": "ativo", "salario_base": 2000},
        1,
    )
    jornada = crud_jornadas.criar_jornada(db, {"nome": "Ponto 44h", "tolerancia_entrada_minutos": 5, "tolerancia_saida_minutos": 5}, 1)
    crud_jornadas.criar_turno(
        db,
        jornada.id,
        {"dia_semana": date.today().weekday(), "hora_entrada": "08:00", "hora_saida_intervalo": "12:00", "hora_retorno_intervalo": "13:00", "hora_saida": "17:00"},
        1,
    )
    crud_jornadas.vincular_jornada_colaborador(db, colaborador.id, {"jornada_id": jornada.id, "data_inicio": date.today() - timedelta(days=1)}, 1)
    return colaborador


def test_marcacao_manual_registra_auditoria(db):
    colaborador = _setup_colaborador_com_jornada(db)
    marcacao = crud_ponto.criar_marcacao(db, {"colaborador_id": colaborador.id, "data": date.today(), "tipo": "entrada", "horario": "08:00", "origem": "manual"}, 1)
    logs = list_audit_logs(db, tabela="marcacoes_ponto", acao="marcacao_manual")
    assert marcacao.id is not None
    assert len(logs) == 1


def test_marcacao_duplicada_bloqueia(db):
    colaborador = _setup_colaborador_com_jornada(db)
    crud_ponto.criar_marcacao(db, {"colaborador_id": colaborador.id, "data": date.today(), "tipo": "entrada", "horario": "08:00", "origem": "manual"}, 1)
    try:
        crud_ponto.criar_marcacao(db, {"colaborador_id": colaborador.id, "data": date.today(), "tipo": "entrada", "horario": "08:00", "origem": "manual"}, 1)
        assert False, "Esperava bloqueio de marcacao duplicada."
    except ValueError as exc:
        assert "duplicada" in str(exc)


def test_colaborador_desligado_nao_recebe_ponto_apos_data(db):
    colaborador = crud_colaboradores.criar(
        db,
        {
            "nome_completo": "Desligado",
            "cpf": "90000000033",
            "regime_contratual": "CLT",
            "status": "desligado",
            "data_desligamento": date.today(),
            "salario_base": 2000,
        },
        1,
    )
    try:
        crud_ponto.criar_marcacao(db, {"colaborador_id": colaborador.id, "data": date.today() + timedelta(days=1), "tipo": "entrada", "horario": "08:00", "origem": "manual"}, 1)
        assert False, "Esperava bloqueio para colaborador desligado."
    except ValueError as exc:
        assert "desligado" in str(exc).lower()
