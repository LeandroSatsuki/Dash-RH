from operational_app import app as operational_app


def test_home_pages_fase5_registradas():
    assert "Tarefas" in operational_app.PAGES
    assert "Notificacoes" in operational_app.PAGES
    assert "Calendario Operacional" in operational_app.PAGES
    assert "Relatorios Operacionais" in operational_app.PAGES
