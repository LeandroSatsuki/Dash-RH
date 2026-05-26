from datetime import date

from src.crud import colaboradores as crud_colaboradores
from src.crud import jornadas as crud_jornadas
from src.services.historico import listar_historico_colaborador


def _colaborador(db):
    return crud_colaboradores.criar(
        db,
        {"nome_completo": "Jornada Demo", "cpf": "90000000031", "regime_contratual": "CLT", "status": "ativo", "salario_base": 2000},
        1,
    )


def test_cria_jornada_com_decimal(db):
    jornada = crud_jornadas.criar_jornada(db, {"nome": "44h", "carga_horaria_semanal": "44", "carga_horaria_diaria": "8"}, 1)
    assert str(jornada.carga_horaria_semanal) == "44.00"


def test_turno_invalido_sem_noturno_bloqueia(db):
    jornada = crud_jornadas.criar_jornada(db, {"nome": "Diurna"}, 1)
    try:
        crud_jornadas.criar_turno(db, jornada.id, {"dia_semana": 0, "hora_entrada": "18:00", "hora_saida": "06:00"}, 1)
        assert False, "Era esperado erro para turno invalido."
    except ValueError as exc:
        assert "saida" in str(exc)


def test_vincular_jornada_cria_historico(db):
    colaborador = _colaborador(db)
    jornada = crud_jornadas.criar_jornada(db, {"nome": "Escala A"}, 1)
    crud_jornadas.vincular_jornada_colaborador(db, colaborador.id, {"jornada_id": jornada.id, "data_inicio": date.today()}, 1)
    historico = listar_historico_colaborador(db, colaborador.id)
    assert any(item.tipo_evento == "alteracao_jornada" for item in historico)
