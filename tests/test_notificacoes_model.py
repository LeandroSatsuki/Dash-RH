from src.crud import notificacoes as crud_notificacoes
from src.db.models import ConfiguracaoNotificacao, Notificacao
from src.services import notification_service


def test_notificacao_model_import_and_table_name():
    assert Notificacao.__tablename__ == "notificacoes"
    assert ConfiguracaoNotificacao.__tablename__ == "configuracoes_notificacao"


def test_notificacao_listar_vazia_em_banco_limpo(db):
    notificacoes = crud_notificacoes.listar(db, usuario_id=1)
    assert notificacoes == []


def test_notificacao_criar_listar_e_marcar_lida(db):
    item = notification_service.notify_user(
        db,
        usuario_id=1,
        titulo="Teste notificacao",
        mensagem="Mensagem de teste",
        tipo="sistema",
    )
    assert item.id is not None

    nao_lidas = crud_notificacoes.listar(db, usuario_id=1, apenas_nao_lidas=True)
    assert len(nao_lidas) == 1

    atualizado = crud_notificacoes.marcar_lida(db, item.id, usuario_id=1)
    assert atualizado.lida is True

    nao_lidas_depois = crud_notificacoes.listar(db, usuario_id=1, apenas_nao_lidas=True)
    assert nao_lidas_depois == []
