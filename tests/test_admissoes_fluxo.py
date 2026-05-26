from datetime import date

from src.crud import admissoes as crud_admissoes
from src.crud import cargos as crud_cargos
from src.crud import centros_custo as crud_centros
from src.crud import colaboradores as crud_colaboradores
from src.crud import departamentos as crud_departamentos
from src.services.audit_service import list_audit_logs
from src.services.historico import listar_historico_colaborador


def _base_colaborador(db):
    dept = crud_departamentos.criar(db, {"nome": "DP Teste"}, 1)
    cargo = crud_cargos.criar(db, {"nome": "Analista", "departamento_id": dept.id}, 1)
    centro = crud_centros.criar(db, {"codigo": "CC001", "nome": "Centro"}, 1)
    colaborador = crud_colaboradores.criar(
        db,
        {
            "nome_completo": "Colaborador Fake",
            "cpf": "90000000001",
            "rg": "RG-FAKE",
            "regime_contratual": "CLT",
            "cargo_id": cargo.id,
            "departamento_id": dept.id,
            "centro_custo_id": centro.id,
            "salario_base": "2500,00",
            "status": "pre_admissao",
        },
        1,
    )
    return colaborador


def test_cria_admissao(db):
    colaborador = _base_colaborador(db)
    admissao = crud_admissoes.criar(db, {"colaborador_id": colaborador.id, "data_admissao": date(2026, 1, 10)}, 1)
    assert admissao.id is not None


def test_checklist_parcial_muda_status(db):
    colaborador = _base_colaborador(db)
    admissao = crud_admissoes.criar(db, {"colaborador_id": colaborador.id, "data_admissao": date(2026, 1, 10), "checklist_json": {"cpf": True}}, 1)
    assert admissao.status in {"documentos_pendentes", "exame_pendente", "contrato_pendente"}


def test_bloqueia_conclusao_sem_checklist_completo(db):
    colaborador = _base_colaborador(db)
    admissao = crud_admissoes.criar(db, {"colaborador_id": colaborador.id, "data_admissao": date(2026, 1, 10), "checklist_json": {"cpf": True, "rg": True}}, 1)
    try:
        crud_admissoes.concluir(db, admissao.id, 1)
        assert False, "Era esperado bloqueio"
    except ValueError as exc:
        assert "checklist" in str(exc)


def test_conclusao_ativa_colaborador_e_cria_historico(db):
    colaborador = _base_colaborador(db)
    checklist = {field: True for field in crud_admissoes.CHECKLIST_FIELDS}
    admissao = crud_admissoes.criar(db, {"colaborador_id": colaborador.id, "data_admissao": date(2026, 1, 10), "checklist_json": checklist}, 1)
    crud_admissoes.concluir(db, admissao.id, 1)
    atualizado = crud_colaboradores.buscar_por_id(db, colaborador.id)
    historico = listar_historico_colaborador(db, colaborador.id)
    assert atualizado.status == "ativo"
    assert any(item.tipo_evento == "admissao" for item in historico)


def test_cancelamento_gera_auditoria(db):
    colaborador = _base_colaborador(db)
    admissao = crud_admissoes.criar(db, {"colaborador_id": colaborador.id, "data_admissao": date(2026, 1, 10)}, 1)
    crud_admissoes.cancelar(db, admissao.id, 1)
    logs = list_audit_logs(db, tabela="admissoes", acao="cancelar_admissao")
    assert len(logs) == 1
