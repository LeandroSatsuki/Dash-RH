from datetime import date

from src.services.historico import listar_historico_colaborador, registrar_historico


def test_registra_historico(db):
    evento = registrar_historico(db, colaborador_id=1, tipo_evento="alteracao_cadastral", data_evento=date(2026, 1, 1), usuario_id=1, campo_alterado="email", valor_anterior="a", valor_novo="b")
    assert evento.id is not None


def test_lista_historico_ordenado(db):
    registrar_historico(db, colaborador_id=1, tipo_evento="alteracao_cadastral", data_evento=date(2026, 1, 1), usuario_id=1)
    registrar_historico(db, colaborador_id=1, tipo_evento="desligamento", data_evento=date(2026, 2, 1), usuario_id=1)
    itens = listar_historico_colaborador(db, 1)
    assert itens[0].data_evento >= itens[-1].data_evento
