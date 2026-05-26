from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from src.crud import folha as crud_folha
from src.db.models import Colaborador, ColaboradorBeneficio, Documento, Ferias, Afastamento
from src.services.indicadores import ferias_vencidas
from src.services.validacoes_dp import digits_only


def _issue(tipo: str, severidade: str, entidade: str, entidade_id: int | None, detalhe: str, recomendacao: str) -> dict:
    return {
        "tipo": tipo,
        "severidade": severidade,
        "entidade": entidade,
        "entidade_id": entidade_id,
        "detalhe": detalhe,
        "recomendacao": recomendacao,
    }


def _cpf_valido(cpf: str | None) -> bool:
    digits = digits_only(cpf)
    return len(digits) == 11


def generate_operational_quality_report(db: Session) -> list[dict]:
    issues: list[dict] = []
    colaboradores = db.query(Colaborador).filter(Colaborador.deletado_em.is_(None)).all()
    today = date.today()
    for item in colaboradores:
        if (item.regime_contratual or "").upper() == "CLT" and not digits_only(item.cpf):
            issues.append(_issue("CPF ausente para CLT", "crítica", "colaborador", item.id, item.nome_completo, "Preencher CPF obrigatório."))
        elif item.cpf and not _cpf_valido(item.cpf):
            issues.append(_issue("CPF inválido", "alta", "colaborador", item.id, item.nome_completo, "Corrigir CPF do colaborador."))
        if item.status == "ativo" and item.data_desligamento is not None:
            issues.append(_issue("Ativo com desligamento", "alta", "colaborador", item.id, item.nome_completo, "Revisar status ou data de desligamento."))
        if item.status == "desligado" and item.data_desligamento is None:
            issues.append(_issue("Desligado sem data", "alta", "colaborador", item.id, item.nome_completo, "Informar data de desligamento."))
        if item.salario_base is None:
            issues.append(_issue("Salário ausente", "média", "colaborador", item.id, item.nome_completo, "Informar salário base."))
        elif item.salario_base < 0:
            issues.append(_issue("Salário negativo", "crítica", "colaborador", item.id, item.nome_completo, "Corrigir salário negativo."))
        if item.cargo_id is None:
            issues.append(_issue("Cargo ausente", "média", "colaborador", item.id, item.nome_completo, "Vincular cargo."))
        if item.departamento_id is None:
            issues.append(_issue("Departamento ausente", "média", "colaborador", item.id, item.nome_completo, "Vincular departamento."))
        if item.centro_custo_id is None:
            issues.append(_issue("Centro de custo ausente", "média", "colaborador", item.id, item.nome_completo, "Vincular centro de custo."))
    for item in db.query(Ferias).filter(Ferias.deletado_em.is_(None)).all():
        if item.data_limite_gozo and item.data_limite_gozo < today and item.status != "concluida":
            issues.append(_issue("Férias vencidas", "alta", "ferias", item.id, f"Colaborador {item.colaborador_id}", "Planejar ou concluir férias."))
    for item in db.query(Afastamento).filter(Afastamento.deletado_em.is_(None)).all():
        if item.data_fim and item.data_fim < item.data_inicio:
            issues.append(_issue("Afastamento com data inválida", "crítica", "afastamento", item.id, f"Colaborador {item.colaborador_id}", "Corrigir período do afastamento."))
    for item in db.query(ColaboradorBeneficio).all():
        if item.status == "ativo" and item.data_inicio is None:
            issues.append(_issue("Benefício ativo sem data_inicio", "média", "beneficio", item.id, f"Colaborador {item.colaborador_id}", "Informar data de início."))
    for item in crud_folha.listar_lancamentos(db):
        comp = crud_folha.buscar_competencia(db, item.competencia_id)
        if comp and comp.status == "fechada":
            issues.append(_issue("Lançamento em competência fechada", "alta", "lancamento_folha", item.id, f"Competência {comp.competencia}", "Reabrir a competência antes de editar."))
    for item in db.query(Documento).filter(Documento.deletado_em.is_(None)).all():
        if item.validade and item.validade < today:
            issues.append(_issue("Documento vencido", "alta", "documento", item.id, item.nome_original, "Atualizar documento vencido."))
    return issues
