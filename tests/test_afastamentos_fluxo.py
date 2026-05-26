from datetime import date

from src.crud import afastamentos as crud_afastamentos
from src.crud import colaboradores as crud_colaboradores
from src.services.audit_service import list_audit_logs
from src.services.historico import listar_historico_colaborador


def _colaborador(db):
    return crud_colaboradores.criar(db, {"nome_completo": "Afastamento Fake", "cpf": "90000000003", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)


def test_registro_calcula_dias(db):
    colaborador = _colaborador(db)
    afastamento = crud_afastamentos.criar(db, {"colaborador_id": colaborador.id, "tipo": "atestado_medico", "data_inicio": date(2026, 3, 1), "data_fim": date(2026, 3, 3)}, 1)
    assert afastamento.quantidade_dias == 3.0


def test_registro_altera_status_colaborador(db):
    colaborador = _colaborador(db)
    crud_afastamentos.criar(db, {"colaborador_id": colaborador.id, "tipo": "inss", "data_inicio": date(2026, 3, 1), "data_fim": date(2026, 3, 3)}, 1)
    atualizado = crud_colaboradores.buscar_por_id(db, colaborador.id)
    assert atualizado.status == "afastado"


def test_encerramento_retorna_colaborador_e_historico(db):
    colaborador = _colaborador(db)
    afastamento = crud_afastamentos.criar(db, {"colaborador_id": colaborador.id, "tipo": "inss", "data_inicio": date(2026, 3, 1), "data_fim": date(2026, 3, 3)}, 1)
    crud_afastamentos.encerrar(db, afastamento.id, date(2026, 3, 4), 1)
    atualizado = crud_colaboradores.buscar_por_id(db, colaborador.id)
    historico = listar_historico_colaborador(db, colaborador.id)
    assert atualizado.status == "ativo"
    assert any(item.tipo_evento == "retorno_afastamento" for item in historico)


def test_anexar_documento_gera_auditoria(tmp_path, db, monkeypatch):
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    colaborador = _colaborador(db)
    afastamento = crud_afastamentos.criar(db, {"colaborador_id": colaborador.id, "tipo": "atestado_medico", "data_inicio": date(2026, 3, 1), "data_fim": date(2026, 3, 3)}, 1)
    documento = crud_afastamentos.anexar_documento(db, afastamento_id=afastamento.id, original_name="atestado.pdf", content=b"fake", usuario_id=1)
    logs = list_audit_logs(db, tabela="documentos", acao="upload_documento_afastamento")
    assert documento.id is not None
    assert len(logs) == 1
