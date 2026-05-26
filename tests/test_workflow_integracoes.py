from datetime import date

from src.crud import colaboradores as crud_colaboradores
from src.crud import documentos_obrigatorios as crud_docs
from src.crud import ferias as crud_ferias
from src.crud import folha as crud_folha
from src.crud import ponto as crud_ponto
from src.crud import workflows as crud_workflows
from src.db.models import ConfiguracaoSistema


def test_ferias_cria_workflow_na_solicitacao(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Ferias WF", "cpf": "90000000051", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)
    ferias = crud_ferias.criar(db, {"colaborador_id": colaborador.id, "data_inicio": date.today(), "data_fim": date.today(), "status": "planejada"}, 1)
    instancia = crud_workflows.buscar_instancia_por_entidade(db, "ferias", ferias.id)
    assert instancia is not None


def test_ajuste_ponto_cria_workflow(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Ponto WF", "cpf": "90000000052", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)
    ajuste = crud_ponto.criar_ajuste(db, {"colaborador_id": colaborador.id, "data": date.today(), "tipo_ajuste": "inclusao", "motivo": "Ajuste", "valor_novo": "08:00"}, 1)
    instancia = crud_workflows.buscar_instancia_por_entidade(db, "ajuste_ponto", ajuste.id)
    assert instancia is not None


def test_fechamento_folha_pode_exigir_aprovacao(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Folha WF", "cpf": "90000000053", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)
    rubrica = crud_folha.criar_rubrica(db, {"codigo": "SALWF", "descricao": "Salario", "tipo": "provento"}, 1)
    competencia = crud_folha.criar_competencia(db, {"ano": 2026, "mes": 10, "competencia": "2026-10"}, 1)
    crud_folha.criar_lancamento(db, {"competencia_id": competencia.id, "colaborador_id": colaborador.id, "rubrica_id": rubrica.id, "tipo": "provento", "valor": "1000,00"}, 1)
    db.add(ConfiguracaoSistema(chave="exigir_aprovacao_fechamento_folha", valor="true"))
    db.commit()
    try:
        crud_folha.fechar_competencia(db, competencia.id, 1)
        assert False, "Era esperado bloqueio por aprovacao."
    except ValueError as exc:
        assert "aprovacao" in str(exc).lower()


def test_dispensa_documento_cria_workflow(db):
    colaborador = crud_colaboradores.criar(db, {"nome_completo": "Doc WF", "cpf": "90000000054", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000}, 1)
    tipo = crud_docs.criar_tipo_documento(db, {"nome": "doc_wf", "ativo": True}, 1)
    crud_docs.criar_regra(db, {"tipo_documento_id": tipo.id, "regime_contratual": "CLT", "obrigatorio": True}, 1)
    pendencia = crud_docs.gerar_pendencias(db, 1)[0]
    crud_docs.dispensar_pendencia(db, pendencia.id, "Justificado", 1)
    instancia = crud_workflows.buscar_instancia_por_entidade(db, "documento_pendencia_dispensa", pendencia.id)
    assert instancia is not None
