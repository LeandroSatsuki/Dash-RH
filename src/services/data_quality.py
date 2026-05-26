from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from src.crud import banco_horas as crud_banco_horas
from src.crud import folha as crud_folha
from src.crud import jornadas as crud_jornadas
from src.db.models import (
    Afastamento,
    ApuracaoPonto,
    Colaborador,
    ColaboradorBeneficio,
    ColaboradorTreinamentoSST,
    CompetenciaFolha,
    Documento,
    DocumentoPendencia,
    EPI,
    ExameOcupacional,
    Ferias,
)
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
    return len(digits_only(cpf)) == 11


def generate_operational_quality_report(db: Session) -> list[dict]:
    issues: list[dict] = []
    colaboradores = db.query(Colaborador).filter(Colaborador.deletado_em.is_(None)).all()
    today = date.today()
    for item in colaboradores:
        if (item.regime_contratual or "").upper() == "CLT" and not digits_only(item.cpf):
            issues.append(_issue("CPF ausente para CLT", "critica", "colaborador", item.id, item.nome_completo, "Preencher CPF obrigatorio."))
        elif item.cpf and not _cpf_valido(item.cpf):
            issues.append(_issue("CPF inválido", "alta", "colaborador", item.id, item.nome_completo, "Corrigir CPF do colaborador."))
        if item.status == "ativo" and item.data_desligamento is not None:
            issues.append(_issue("Ativo com desligamento", "alta", "colaborador", item.id, item.nome_completo, "Revisar status ou data de desligamento."))
        if item.status == "desligado" and item.data_desligamento is None:
            issues.append(_issue("Desligado sem data", "alta", "colaborador", item.id, item.nome_completo, "Informar data de desligamento."))
        if item.salario_base is None:
            issues.append(_issue("Salário ausente", "media", "colaborador", item.id, item.nome_completo, "Informar salario base."))
        elif item.salario_base < 0:
            issues.append(_issue("Salário negativo", "critica", "colaborador", item.id, item.nome_completo, "Corrigir salario negativo."))
        if item.cargo_id is None:
            issues.append(_issue("Cargo ausente", "media", "colaborador", item.id, item.nome_completo, "Vincular cargo."))
        if item.departamento_id is None:
            issues.append(_issue("Departamento ausente", "media", "colaborador", item.id, item.nome_completo, "Vincular departamento."))
        if item.centro_custo_id is None:
            issues.append(_issue("Centro de custo ausente", "media", "colaborador", item.id, item.nome_completo, "Vincular centro de custo."))
        if item.status == "ativo" and crud_jornadas.jornada_atual_colaborador(db, item.id) is None:
            issues.append(_issue("Colaborador ativo sem jornada", "alta", "colaborador", item.id, item.nome_completo, "Vincular jornada ativa ao colaborador."))
        saldo = crud_banco_horas.saldo_colaborador(db, item.id)
        if saldo > 100 or saldo < -40:
            issues.append(_issue("Banco de horas acima do limite", "media", "colaborador", item.id, item.nome_completo, "Revisar saldo de banco de horas."))
    for item in db.query(Ferias).filter(Ferias.deletado_em.is_(None)).all():
        if item.data_limite_gozo and item.data_limite_gozo < today and item.status != "concluida":
            issues.append(_issue("Férias vencidas", "alta", "ferias", item.id, f"Colaborador {item.colaborador_id}", "Planejar ou concluir ferias."))
    for item in db.query(Afastamento).filter(Afastamento.deletado_em.is_(None)).all():
        if item.data_fim and item.data_fim < item.data_inicio:
            issues.append(_issue("Afastamento com data invalida", "critica", "afastamento", item.id, f"Colaborador {item.colaborador_id}", "Corrigir periodo do afastamento."))
        if item.status == "ativo" and item.data_fim is None and (today - item.data_inicio).days > 30:
            issues.append(_issue("Afastamento sem retorno previsto", "media", "afastamento", item.id, f"Colaborador {item.colaborador_id}", "Informar retorno previsto ou encerrar afastamento."))
    for item in db.query(ColaboradorBeneficio).all():
        if item.status == "ativo" and item.data_inicio is None:
            issues.append(_issue("Beneficio ativo sem data_inicio", "media", "beneficio", item.id, f"Colaborador {item.colaborador_id}", "Informar data de inicio."))
    for item in crud_folha.listar_lancamentos(db):
        comp = crud_folha.buscar_competencia(db, item.competencia_id)
        if comp and comp.status == "fechada":
            issues.append(_issue("Lancamento em competencia fechada", "alta", "lancamento_folha", item.id, f"Competencia {comp.competencia}", "Reabrir a competencia antes de editar."))
    for item in db.query(Documento).filter(Documento.deletado_em.is_(None)).all():
        if item.validade and item.validade < today:
            issues.append(_issue("Documento vencido", "alta", "documento", item.id, item.nome_original, "Atualizar documento vencido."))
    for item in db.query(DocumentoPendencia).all():
        if item.status in {"pendente", "vencido"}:
            label = "Documento obrigatorio pendente" if item.status == "pendente" else "Documento obrigatorio vencido"
            issues.append(_issue(label, item.severidade, "documento_pendencia", item.id, f"Colaborador {item.colaborador_id}", "Regularizar documento obrigatorio."))
    for item in db.query(ExameOcupacional).all():
        if item.data_validade and item.data_validade < today:
            issues.append(_issue("Exame ocupacional vencido", "alta", "exame_ocupacional", item.id, f"Colaborador {item.colaborador_id}", "Renovar exame ocupacional."))
    for item in db.query(ColaboradorTreinamentoSST).all():
        if item.data_validade and item.data_validade < today:
            issues.append(_issue("Treinamento vencido", "media", "treinamento_sst", item.id, f"Colaborador {item.colaborador_id}", "Atualizar treinamento SST."))
    for item in db.query(EPI).all():
        if item.validade_ca and item.validade_ca < today:
            issues.append(_issue("EPI com CA vencido", "alta", "epi", item.id, item.nome, "Revalidar CA ou substituir EPI."))
    for item in db.query(ApuracaoPonto).all():
        if item.status == "inconsistente":
            issues.append(_issue("Ponto inconsistente", "alta", "apuracao_ponto", item.id, f"Colaborador {item.colaborador_id} em {item.data.isoformat()}", "Conferir marcacoes e ajustar ponto."))
    for item in db.query(CompetenciaFolha).filter(CompetenciaFolha.status.in_(["aberta", "reaberta", "em_conferencia"])).all():
        if item.data_abertura and (today - item.data_abertura.date()).days > 45:
            issues.append(_issue("Competencia antiga aberta", "alta", "competencia_folha", item.id, item.competencia, "Fechar ou revisar competencia em aberto."))
    return issues
