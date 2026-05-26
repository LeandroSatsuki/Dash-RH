from src.auth.permissions import has_permission


def test_dp_tem_permissoes_fase4():
    assert has_permission("dp", "jornadas:create")
    assert has_permission("dp", "ponto:approve")
    assert has_permission("dp", "sst:update")


def test_gestor_nao_tem_permissao_sst_create():
    assert has_permission("gestor", "ponto:view")
    assert not has_permission("gestor", "sst:create")


def test_visualizador_tem_apenas_alerta_view_e_nao_update():
    assert has_permission("visualizador", "alertas:view")
    assert not has_permission("visualizador", "alertas:update")
