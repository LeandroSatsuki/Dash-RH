from src.auth.users import authenticate_user
from src.services.audit_service import compare_changes, list_audit_logs, log_action, log_sensitive_view


def test_compare_changes_sanitiza_campos():
    changes = compare_changes({"cpf": "12345678901", "nome": "A"}, {"cpf": "99999999999", "nome": "B"})
    assert any(change["campo"] == "cpf" and "***" in change["valor_novo"] for change in changes)


def test_log_action_e_listagem(db):
    log_action(db, tabela="teste", acao="create", usuario_id=1, valor_novo={"cpf": "12345678901"})
    logs = list_audit_logs(db, tabela="teste")
    assert len(logs) >= 1
    assert "***" in (logs[0].valor_novo or "")


def test_login_sucesso_e_falha_geram_auditoria(db):
    assert authenticate_user(db, "admin@test.local", "123456") is not None
    assert authenticate_user(db, "admin@test.local", "errada") is None
    logs = list_audit_logs(db, tabela="usuarios")
    actions = {item.acao for item in logs}
    assert "login" in actions
    assert "login_failed" in actions


def test_visualizacao_sensivel_gera_auditoria(db):
    log_sensitive_view(db, tabela="colaboradores", registro_id=10, usuario_id=1, campos=["cpf", "salario_base"])
    logs = list_audit_logs(db, tabela="colaboradores", acao="view_sensitive_data")
    assert len(logs) == 1
    assert "campos" in (logs[0].valor_novo or "")
