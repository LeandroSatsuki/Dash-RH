from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import (
    Alerta,
    Afastamento,
    ApuracaoPonto,
    ColaboradorTreinamentoSST,
    CompetenciaFolha,
    DocumentoPendencia,
    EPI,
    ExameOcupacional,
    Ferias,
)
from src.services.audit_service import log_action
from src.services.data_quality import generate_operational_quality_report


def upsert_alerta(
    db: Session,
    *,
    tipo: str,
    severidade: str,
    titulo: str,
    descricao: str,
    entidade_tipo: str | None = None,
    entidade_id: int | None = None,
) -> Alerta:
    existente = db.scalar(
        select(Alerta).where(
            Alerta.tipo == tipo,
            Alerta.entidade_tipo == entidade_tipo,
            Alerta.entidade_id == entidade_id,
            Alerta.status.in_(["aberto", "em_analise"]),
        )
    )
    if existente is not None:
        existente.severidade = severidade
        existente.titulo = titulo
        existente.descricao = descricao
        db.add(existente)
        db.commit()
        db.refresh(existente)
        return existente
    alerta = Alerta(
        tipo=tipo,
        severidade=severidade,
        titulo=titulo,
        descricao=descricao,
        entidade_tipo=entidade_tipo,
        entidade_id=entidade_id,
        status="aberto",
    )
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta


def gerar_alertas(db: Session) -> list[Alerta]:
    today = date.today()
    created: list[Alerta] = []
    for pendencia in db.scalars(select(DocumentoPendencia)).all():
        if pendencia.status in {"pendente", "vencido"}:
            created.append(
                upsert_alerta(
                    db,
                    tipo="documento_obrigatorio_pendente" if pendencia.status == "pendente" else "documento_vencido",
                    severidade=pendencia.severidade,
                    titulo="Pendencia de documento obrigatorio",
                    descricao=f"Documento obrigatorio do colaborador {pendencia.colaborador_id} esta com status {pendencia.status}.",
                    entidade_tipo="documento_pendencia",
                    entidade_id=pendencia.id,
                )
            )
    for exame in db.scalars(select(ExameOcupacional)).all():
        if exame.data_validade and exame.data_validade < today:
            created.append(
                upsert_alerta(
                    db,
                    tipo="exame_ocupacional_vencido",
                    severidade="alta",
                    titulo="Exame ocupacional vencido",
                    descricao=f"Exame {exame.tipo_exame} do colaborador {exame.colaborador_id} esta vencido.",
                    entidade_tipo="exame_ocupacional",
                    entidade_id=exame.id,
                )
            )
    for treinamento in db.scalars(select(ColaboradorTreinamentoSST)).all():
        if treinamento.data_validade and treinamento.data_validade < today:
            created.append(
                upsert_alerta(
                    db,
                    tipo="treinamento_vencido",
                    severidade="media",
                    titulo="Treinamento SST vencido",
                    descricao=f"O treinamento {treinamento.treinamento_id} do colaborador {treinamento.colaborador_id} esta vencido.",
                    entidade_tipo="colaborador_treinamento_sst",
                    entidade_id=treinamento.id,
                )
            )
    for item in db.execute(select(EPI.id, EPI.validade_ca).where(EPI.validade_ca.is_not(None))).all():
        if item.validade_ca and item.validade_ca < today:
            created.append(
                upsert_alerta(
                    db,
                    tipo="ca_epi_vencido",
                    severidade="media",
                    titulo="CA de EPI vencido",
                    descricao=f"O EPI {item.id} possui CA vencido.",
                    entidade_tipo="epi",
                    entidade_id=item.id,
                )
            )
    for ferias in db.scalars(select(Ferias).where(Ferias.deletado_em.is_(None))).all():
        if ferias.data_limite_gozo and ferias.data_limite_gozo < today and ferias.status != "concluida":
            created.append(
                upsert_alerta(
                    db,
                    tipo="ferias_vencidas",
                    severidade="alta",
                    titulo="Ferias vencidas",
                    descricao=f"O colaborador {ferias.colaborador_id} possui ferias vencidas.",
                    entidade_tipo="ferias",
                    entidade_id=ferias.id,
                )
            )
        elif ferias.data_limite_gozo and 0 <= (ferias.data_limite_gozo - today).days <= 30:
            created.append(
                upsert_alerta(
                    db,
                    tipo="ferias_a_vencer",
                    severidade="media",
                    titulo="Ferias a vencer",
                    descricao=f"O colaborador {ferias.colaborador_id} possui ferias a vencer em ate 30 dias.",
                    entidade_tipo="ferias",
                    entidade_id=ferias.id,
                )
            )
    for afastamento in db.scalars(select(Afastamento).where(Afastamento.status == "ativo")).all():
        if afastamento.data_fim is None and (today - afastamento.data_inicio).days > 30:
            created.append(
                upsert_alerta(
                    db,
                    tipo="afastamento_sem_retorno",
                    severidade="media",
                    titulo="Afastamento sem retorno",
                    descricao=f"O afastamento {afastamento.id} segue ativo sem data final.",
                    entidade_tipo="afastamento",
                    entidade_id=afastamento.id,
                )
            )
    for apuracao in db.scalars(select(ApuracaoPonto).where(ApuracaoPonto.status == "inconsistente")).all():
        created.append(
            upsert_alerta(
                db,
                tipo="ponto_inconsistente",
                severidade="alta",
                titulo="Ponto inconsistente",
                descricao=f"A apuracao de ponto do colaborador {apuracao.colaborador_id} em {apuracao.data.isoformat()} esta inconsistente.",
                entidade_tipo="apuracao_ponto",
                entidade_id=apuracao.id,
            )
        )
    limite_competencia = today - timedelta(days=45)
    for competencia in db.scalars(select(CompetenciaFolha).where(CompetenciaFolha.status.in_(["aberta", "reaberta", "em_conferencia"]))).all():
        if competencia.data_abertura and competencia.data_abertura.date() < limite_competencia:
            created.append(
                upsert_alerta(
                    db,
                    tipo="competencia_folha_aberta_antiga",
                    severidade="alta",
                    titulo="Competencia aberta ha muito tempo",
                    descricao=f"A competencia {competencia.competencia} permanece aberta ha mais de 45 dias.",
                    entidade_tipo="competencia_folha",
                    entidade_id=competencia.id,
                )
            )
    for issue in generate_operational_quality_report(db):
        if issue["severidade"] == "critica":
            created.append(
                upsert_alerta(
                    db,
                    tipo="qualidade_critica",
                    severidade="critica",
                    titulo=issue["tipo"],
                    descricao=issue["detalhe"],
                    entidade_tipo=issue["entidade"],
                    entidade_id=issue["entidade_id"],
                )
            )
    return created


def listar_alertas(
    db: Session,
    *,
    severidade: str | None = None,
    tipo: str | None = None,
    status: str | None = None,
) -> list[Alerta]:
    stmt = select(Alerta)
    if severidade:
        stmt = stmt.where(Alerta.severidade == severidade)
    if tipo:
        stmt = stmt.where(Alerta.tipo == tipo)
    if status:
        stmt = stmt.where(Alerta.status == status)
    stmt = stmt.order_by(Alerta.criado_em.desc())
    return list(db.scalars(stmt).all())


def resolver_alerta(db: Session, alerta_id: int, usuario_id: int | None = None, justificativa: str | None = None) -> Alerta:
    alerta = db.get(Alerta, alerta_id)
    if alerta is None:
        raise ValueError("Alerta nao encontrado.")
    alerta.status = "resolvido"
    alerta.resolvido_em = datetime.now(UTC).replace(tzinfo=None)
    alerta.usuario_responsavel_id = usuario_id
    alerta.justificativa = justificativa
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    log_action(db, tabela="alertas", acao="resolver_alerta", registro_id=alerta.id, usuario_id=usuario_id, origem="alertas")
    return alerta


def ignorar_alerta(db: Session, alerta_id: int, usuario_id: int | None = None, justificativa: str | None = None) -> Alerta:
    alerta = db.get(Alerta, alerta_id)
    if alerta is None:
        raise ValueError("Alerta nao encontrado.")
    alerta.status = "ignorado"
    alerta.resolvido_em = datetime.now(UTC).replace(tzinfo=None)
    alerta.usuario_responsavel_id = usuario_id
    alerta.justificativa = justificativa
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    log_action(db, tabela="alertas", acao="ignorar_alerta", registro_id=alerta.id, usuario_id=usuario_id, origem="alertas")
    return alerta
