from src.crud import notificacoes as crud_notificacoes
from src.services import notification_service


def test_notificacao_interna_criada(db):
    item = notification_service.notify_user(db, usuario_id=1, titulo="Teste", mensagem="Mensagem", tipo="sistema")
    assert item.id is not None


def test_notificacao_marca_lida(db):
    item = notification_service.notify_user(db, usuario_id=1, titulo="Teste", mensagem="Mensagem", tipo="sistema")
    atualizado = notification_service.marcar_lida(db, item.id, 1)
    assert atualizado.lida is True


def test_notificacao_sanitiza_mensagem(db):
    item = notification_service.notify_user(db, usuario_id=1, titulo="CPF 12345678901", mensagem="R$ 2.000,00", tipo="sistema")
    assert "[CPF_MASKED]" in item.titulo
    assert "[MASKED]" in item.mensagem
