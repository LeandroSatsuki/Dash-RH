from src.auth.permissions import has_permission


def test_dp_tem_permissoes_workflow_tarefa_relatorio():
    assert has_permission("dp", "workflows:create")
    assert has_permission("dp", "tarefas:update")
    assert has_permission("dp", "relatorios_operacionais:export")


def test_gestor_tem_aprovacao_mas_nao_exporta_relatorio():
    assert has_permission("gestor", "workflows:approve")
    assert not has_permission("gestor", "relatorios_operacionais:export")


def test_visualizador_nao_tem_tarefa_update():
    assert has_permission("visualizador", "notificacoes:view")
    assert not has_permission("visualizador", "tarefas:update")
