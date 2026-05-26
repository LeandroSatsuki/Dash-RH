from datetime import date, timedelta

from src.crud import colaboradores as crud_colaboradores
from src.crud import documentos_obrigatorios as crud_docs
from src.crud import jornadas as crud_jornadas
from src.crud import ponto as crud_ponto
from src.services import alerts


def test_gera_alerta_de_documento_pendente(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Alerta Doc", "cpf": "90000000037", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)
    tipo = crud_docs.criar_tipo_documento(db, {"nome": "cpf_doc", "ativo": True}, 1)
    crud_docs.criar_regra(db, {"tipo_documento_id": tipo.id, "regime_contratual": "CLT", "obrigatorio": True}, 1)
    crud_docs.gerar_pendencias(db, 1)
    itens = alerts.gerar_alertas(db)
    assert any(item.tipo == "documento_obrigatorio_pendente" for item in itens)


def test_gera_alerta_de_ponto_inconsistente(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Alerta Ponto", "cpf": "90000000038", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)
    jornada = crud_jornadas.criar_jornada(db, {"nome": "Jornada Alerta"}, 1)
    crud_jornadas.criar_turno(db, jornada.id, {"dia_semana": date.today().weekday(), "hora_entrada": "08:00", "hora_saida": "17:00"}, 1)
    crud_jornadas.vincular_jornada_colaborador(db, colaborador.id, {"jornada_id": jornada.id, "data_inicio": date.today() - timedelta(days=1)}, 1)
    crud_ponto.apurar_periodo(db, data_inicio=date.today(), data_fim=date.today(), usuario_id=1)
    itens = alerts.gerar_alertas(db)
    assert any(item.tipo == "ponto_inconsistente" for item in itens)


def test_resolver_alerta_altera_status(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Resolve Alerta", "cpf": "90000000039", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)
    tipo = crud_docs.criar_tipo_documento(db, {"nome": "rg_doc", "ativo": True}, 1)
    crud_docs.criar_regra(db, {"tipo_documento_id": tipo.id, "regime_contratual": "CLT", "obrigatorio": True}, 1)
    crud_docs.gerar_pendencias(db, 1)
    alerta = alerts.gerar_alertas(db)[0]
    atualizado = alerts.resolver_alerta(db, alerta.id, 1, "Tratado")
    assert atualizado.status == "resolvido"
