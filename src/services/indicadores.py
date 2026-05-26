from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.crud import folha as crud_folha
from src.db.models import (
    Afastamento,
    Alerta,
    ApuracaoPonto,
    Beneficio,
    BancoHorasMovimento,
    CentroCusto,
    Colaborador,
    ColaboradorBeneficio,
    CompetenciaFolha,
    Departamento,
    DocumentoPendencia,
    EPI,
    ExameOcupacional,
    Documento,
    Ferias,
    Jornada,
    LancamentoFolha,
    ColaboradorTreinamentoSST,
)


def _safe_divide(numerator: float | int | None, denominator: float | int | None) -> float:
    if denominator in (None, 0):
        return 0.0
    return float(numerator or 0) / float(denominator)


def _colaborador_filters(
    *,
    departamento_id: int | None = None,
    centro_custo_id: int | None = None,
    regime_contratual: str | None = None,
    status: str | None = None,
):
    filters = [Colaborador.deletado_em.is_(None)]
    if departamento_id:
        filters.append(Colaborador.departamento_id == departamento_id)
    if centro_custo_id:
        filters.append(Colaborador.centro_custo_id == centro_custo_id)
    if regime_contratual:
        filters.append(Colaborador.regime_contratual == regime_contratual)
    if status:
        filters.append(Colaborador.status == status)
    return filters


def headcount_ativo(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Colaborador).where(Colaborador.deletado_em.is_(None), Colaborador.status == "ativo")) or 0


def admissoes_no_mes(db: Session, competencia: str) -> int:
    return db.scalar(select(func.count()).select_from(Colaborador).where(Colaborador.deletado_em.is_(None), func.strftime("%Y-%m", Colaborador.data_admissao) == competencia)) or 0


def desligamentos_no_mes(db: Session, competencia: str) -> int:
    return db.scalar(select(func.count()).select_from(Colaborador).where(Colaborador.deletado_em.is_(None), func.strftime("%Y-%m", Colaborador.data_desligamento) == competencia)) or 0


def saldo_headcount(admissoes: int, desligamentos: int) -> int:
    return admissoes - desligamentos


def efetivo_medio(efetivo_inicial: float, efetivo_final: float) -> float:
    return (float(efetivo_inicial or 0) + float(efetivo_final or 0)) / 2


def turnover(admissoes: int, desligamentos: int, efetivo_medio_valor: float) -> float:
    return _safe_divide((admissoes + desligamentos) / 2, efetivo_medio_valor)


def afastamentos_em_dias(db: Session, competencia: str | None = None) -> float:
    stmt = select(func.coalesce(func.sum(Afastamento.quantidade_dias), 0)).where(Afastamento.deletado_em.is_(None))
    if competencia:
        stmt = stmt.where(func.strftime("%Y-%m", Afastamento.data_inicio) == competencia)
    return float(db.scalar(stmt) or 0)


def faltas(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Afastamento).where(Afastamento.deletado_em.is_(None), Afastamento.tipo == "falta_injustificada")) or 0


def ferias_em_aberto(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Ferias).where(Ferias.deletado_em.is_(None), Ferias.status.in_(["planejada", "solicitada", "aprovada", "em_gozo"]))) or 0


def ferias_vencidas(db: Session) -> int:
    today = date.today()
    return db.scalar(select(func.count()).select_from(Ferias).where(Ferias.deletado_em.is_(None), Ferias.data_limite_gozo.is_not(None), Ferias.data_limite_gozo < today, Ferias.status != "concluida")) or 0


def absenteismo(dias_nao_produtivos: float, dias_programados: float) -> float:
    return _safe_divide(dias_nao_produtivos, dias_programados)


def folha_bruta(db: Session, competencia_id: int | None = None) -> float:
    if competencia_id is not None:
        snapshot = crud_folha.buscar_snapshot(db, competencia_id)
        if snapshot is not None:
            return float(snapshot.total_proventos or 0)
    stmt = select(func.coalesce(func.sum(LancamentoFolha.valor), 0)).where(LancamentoFolha.deletado_em.is_(None))
    if competencia_id is not None:
        stmt = stmt.where(LancamentoFolha.competencia_id == competencia_id)
    return float(db.scalar(stmt) or 0)


def total_beneficios(db: Session) -> float:
    return float(db.scalar(select(func.coalesce(func.sum(ColaboradorBeneficio.valor_empresa), 0))) or 0)


def total_encargos(db: Session, competencia_id: int | None = None) -> float:
    if competencia_id is not None:
        snapshot = crud_folha.buscar_snapshot(db, competencia_id)
        if snapshot is not None:
            return float(snapshot.total_encargos or 0)
    stmt = select(func.coalesce(func.sum(LancamentoFolha.valor), 0)).where(LancamentoFolha.deletado_em.is_(None), LancamentoFolha.tipo == "encargo")
    if competencia_id is not None:
        stmt = stmt.where(LancamentoFolha.competencia_id == competencia_id)
    return float(db.scalar(stmt) or 0)


def custo_total_empresa(db: Session, competencia_id: int | None = None) -> float:
    if competencia_id is not None:
        snapshot = crud_folha.buscar_snapshot(db, competencia_id)
        if snapshot is not None:
            return float(snapshot.total_custo_empresa or 0)
    return folha_bruta(db, competencia_id) + total_beneficios(db)


def custo_por_colaborador(db: Session, competencia_id: int | None = None) -> float:
    return _safe_divide(custo_total_empresa(db, competencia_id), headcount_ativo(db))


def colaboradores_com_dados_incompletos(db: Session) -> int:
    return db.scalar(
        select(func.count())
        .select_from(Colaborador)
        .where(
            Colaborador.deletado_em.is_(None),
            (
                Colaborador.cpf.is_(None)
                | Colaborador.salario_base.is_(None)
                | Colaborador.cargo_id.is_(None)
                | Colaborador.departamento_id.is_(None)
            ),
        )
    ) or 0


def indicadores_dashboard(db: Session, competencia: str | None = None) -> dict:
    competencia_obj = None
    if not competencia:
        today = date.today()
        competencia = f"{today.year:04d}-{today.month:02d}"
    adm = admissoes_no_mes(db, competencia)
    desl = desligamentos_no_mes(db, competencia)
    competencia_obj = db.scalar(select(CompetenciaFolha).where(CompetenciaFolha.competencia == competencia))
    hc = headcount_ativo(db)
    efetivo = efetivo_medio(max(hc - adm + desl, 0), hc)
    competencia_id = competencia_obj.id if competencia_obj else None
    return {
        "competencia": competencia,
        "headcount_ativo": hc,
        "admissoes": adm,
        "desligamentos": desl,
        "saldo_headcount": saldo_headcount(adm, desl),
        "efetivo_medio": efetivo,
        "turnover": turnover(adm, desl, efetivo),
        "afastamentos_em_dias": afastamentos_em_dias(db),
        "faltas": faltas(db),
        "ferias_em_aberto": ferias_em_aberto(db),
        "ferias_vencidas": ferias_vencidas(db),
        "folha_bruta": folha_bruta(db, competencia_id),
        "total_beneficios": total_beneficios(db),
        "custo_total_empresa": custo_total_empresa(db, competencia_id),
        "custo_por_colaborador": custo_por_colaborador(db, competencia_id),
        "colaboradores_com_dados_incompletos": colaboradores_com_dados_incompletos(db),
        "documentos_pendentes": db.scalar(select(func.count()).select_from(Documento).where(Documento.deletado_em.is_(None), Documento.status != "ativo")) or 0,
        "alertas_criticos": db.scalar(select(func.count()).select_from(Alerta).where(Alerta.status == "aberto", Alerta.severidade == "critica")) or 0,
    }


def indicadores_operacionais(
    db: Session,
    *,
    ano: int | None = None,
    mes: int | None = None,
    departamento_id: int | None = None,
    centro_custo_id: int | None = None,
    regime_contratual: str | None = None,
    status_colaborador: str | None = None,
) -> dict:
    today = date.today()
    ano = ano or today.year
    mes = mes or today.month
    competencia = f"{ano:04d}-{mes:02d}"
    filters = _colaborador_filters(
        departamento_id=departamento_id,
        centro_custo_id=centro_custo_id,
        regime_contratual=regime_contratual,
        status=status_colaborador,
    )
    colaboradores = list(db.scalars(select(Colaborador).where(*filters)).all())
    competencia_obj = db.scalar(select(CompetenciaFolha).where(CompetenciaFolha.competencia == competencia))
    competencia_id = competencia_obj.id if competencia_obj else None

    ativos = [c for c in colaboradores if c.status == "ativo"]
    admissoes_mes = [c for c in colaboradores if c.data_admissao and c.data_admissao.strftime("%Y-%m") == competencia]
    desligamentos_mes = [c for c in colaboradores if c.data_desligamento and c.data_desligamento.strftime("%Y-%m") == competencia]
    afastados_ativos = [c for c in colaboradores if c.status == "afastado"]
    ferias_vencer = [
        f for f in list_records_like_ferias(db)
        if f.data_limite_gozo and 0 <= (f.data_limite_gozo - today).days <= 90 and _match_colaborador(colaboradores, f.colaborador_id)
    ]

    custo_departamento = defaultdict(float)
    rubrica_totais = defaultdict(float)
    lancamentos = db.scalars(select(LancamentoFolha).where(LancamentoFolha.deletado_em.is_(None))).all()
    colaboradores_map = {c.id: c for c in colaboradores}
    rubricas_map = {r.id: r for r in db.scalars(select(Beneficio)).all()}
    for lancamento in lancamentos:
        colaborador = colaboradores_map.get(lancamento.colaborador_id)
        if colaborador is None:
            continue
        custo_departamento[colaborador.departamento_id or 0] += float(lancamento.valor or 0)
        rubrica_totais[lancamento.rubrica_id] += float(lancamento.valor or 0)

    headcount_por_departamento = []
    departamentos_map = {d.id: d.nome for d in db.scalars(select(Departamento)).all()}
    for dept_id, total in db.execute(
        select(Colaborador.departamento_id, func.count())
        .where(*filters)
        .group_by(Colaborador.departamento_id)
    ).all():
        headcount_por_departamento.append({"departamento": departamentos_map.get(dept_id, "Sem departamento"), "total": int(total or 0)})

    movimentos = []
    for offset in range(5, -1, -1):
        ref = date(ano, mes, 1) - timedelta(days=offset * 30)
        comp = ref.strftime("%Y-%m")
        movimentos.append({"competencia": comp, "admissoes": admissoes_no_mes(db, comp), "desligamentos": desligamentos_no_mes(db, comp)})

    afastamentos_tipo = []
    for tipo, total in db.execute(
        select(Afastamento.tipo, func.count())
        .where(Afastamento.deletado_em.is_(None), func.strftime("%Y-%m", Afastamento.data_inicio) == competencia)
        .group_by(Afastamento.tipo)
    ).all():
        afastamentos_tipo.append({"tipo": tipo, "total": int(total or 0)})

    ferias_status = []
    for status, total in db.execute(
        select(Ferias.status, func.count()).where(Ferias.deletado_em.is_(None)).group_by(Ferias.status)
    ).all():
        ferias_status.append({"status": status, "total": int(total or 0)})

    custo_por_departamento = [
        {"departamento": departamentos_map.get(dept_id, "Sem departamento"), "valor": valor}
        for dept_id, valor in custo_departamento.items()
    ]
    custo_por_rubrica = [{"rubrica_id": rubrica_id, "valor": valor} for rubrica_id, valor in rubrica_totais.items()]
    apuracoes = db.scalars(select(ApuracaoPonto)).all()
    horas_previstas = sum(float(item.horas_previstas or 0) for item in apuracoes if _match_colaborador(colaboradores, item.colaborador_id))
    horas_trabalhadas = sum(float(item.horas_trabalhadas or 0) for item in apuracoes if _match_colaborador(colaboradores, item.colaborador_id))
    horas_extras = sum(float(item.horas_extras or 0) for item in apuracoes if _match_colaborador(colaboradores, item.colaborador_id))
    horas_faltantes = sum(float(item.horas_faltantes or 0) for item in apuracoes if _match_colaborador(colaboradores, item.colaborador_id))
    inconsistencia_count = len([item for item in apuracoes if item.status == "inconsistente" and _match_colaborador(colaboradores, item.colaborador_id)])
    banco_horas_rows = db.scalars(select(BancoHorasMovimento)).all()
    saldo_banco_horas = 0.0
    for item in banco_horas_rows:
        if not _match_colaborador(colaboradores, item.colaborador_id):
            continue
        horas = float(item.horas or 0)
        if item.tipo == "credito":
            saldo_banco_horas += horas
        elif item.tipo == "debito":
            saldo_banco_horas -= horas
        else:
            saldo_banco_horas += horas
    documentos_pendentes = db.scalar(select(func.count()).select_from(DocumentoPendencia).where(DocumentoPendencia.status == "pendente")) or 0
    documentos_vencidos = db.scalar(select(func.count()).select_from(DocumentoPendencia).where(DocumentoPendencia.status == "vencido")) or 0
    exames_vencidos = db.scalar(select(func.count()).select_from(ExameOcupacional).where(ExameOcupacional.data_validade.is_not(None), ExameOcupacional.data_validade < today)) or 0
    treinamentos_vencidos = db.scalar(select(func.count()).select_from(ColaboradorTreinamentoSST).where(ColaboradorTreinamentoSST.data_validade.is_not(None), ColaboradorTreinamentoSST.data_validade < today)) or 0
    epis_pendentes = db.scalar(select(func.count()).select_from(EPI).where(EPI.validade_ca.is_not(None), EPI.validade_ca < today)) or 0
    alertas = db.execute(select(Alerta.severidade, func.count()).group_by(Alerta.severidade)).all()
    alertas_severidade = [{"severidade": severidade, "total": int(total or 0)} for severidade, total in alertas]
    docs_tipo = db.execute(
        select(DocumentoPendencia.tipo_documento_id, func.count()).group_by(DocumentoPendencia.tipo_documento_id)
    ).all()
    documentos_por_tipo = [{"tipo_documento_id": tipo_id, "total": int(total or 0)} for tipo_id, total in docs_tipo]
    exames_tipo = db.execute(
        select(ExameOcupacional.tipo_exame, func.count()).where(ExameOcupacional.data_validade.is_not(None), ExameOcupacional.data_validade < today).group_by(ExameOcupacional.tipo_exame)
    ).all()
    exames_por_tipo = [{"tipo_exame": tipo, "total": int(total or 0)} for tipo, total in exames_tipo]
    banco_por_departamento = defaultdict(float)
    for item in banco_horas_rows:
        colaborador = colaboradores_map.get(item.colaborador_id)
        if colaborador is None:
            continue
        sinal = 1 if item.tipo != "debito" else -1
        banco_por_departamento[colaborador.departamento_id or 0] += sinal * float(item.horas or 0)
    ponto_por_mes = []
    for offset in range(5, -1, -1):
        ref = date(ano, mes, 1) - timedelta(days=offset * 30)
        comp_month = ref.strftime("%Y-%m")
        inconsistencias = db.scalar(
            select(func.count()).select_from(ApuracaoPonto).where(func.strftime("%Y-%m", ApuracaoPonto.data) == comp_month, ApuracaoPonto.status == "inconsistente")
        ) or 0
        ponto_por_mes.append({"competencia": comp_month, "inconsistencias": int(inconsistencias)})
    absenteismo_ponto = _safe_divide(afastamentos_em_dias(db, competencia) + horas_faltantes, max(horas_previstas, 1))

    return {
        "competencia": competencia,
        "kpis": {
            "colaboradores_ativos": len(ativos),
            "admissoes_mes": len(admissoes_mes),
            "desligamentos_mes": len(desligamentos_mes),
            "saldo_headcount": len(admissoes_mes) - len(desligamentos_mes),
            "turnover": turnover(len(admissoes_mes), len(desligamentos_mes), efetivo_medio(max(len(ativos) - len(admissoes_mes) + len(desligamentos_mes), 0), len(ativos))),
            "afastados_ativos": len(afastados_ativos),
            "dias_afastamento_mes": afastamentos_em_dias(db, competencia),
            "ferias_vencidas": ferias_vencidas(db),
            "ferias_a_vencer": len(ferias_vencer),
            "folha_bruta": folha_bruta(db, competencia_id),
            "custo_total_competencia": custo_total_empresa(db, competencia_id),
            "beneficios_ativos": db.scalar(select(func.count()).select_from(ColaboradorBeneficio).where(ColaboradorBeneficio.status == "ativo")) or 0,
            "custo_beneficios": total_beneficios(db),
            "problemas_criticos_qualidade": colaboradores_com_dados_incompletos(db),
            "horas_previstas": horas_previstas,
            "horas_trabalhadas": horas_trabalhadas,
            "horas_extras": horas_extras,
            "horas_faltantes": horas_faltantes,
            "taxa_inconsistencia_ponto": _safe_divide(inconsistencia_count, max(len(apuracoes), 1)),
            "saldo_banco_horas": saldo_banco_horas,
            "documentos_pendentes": int(documentos_pendentes),
            "documentos_vencidos": int(documentos_vencidos),
            "exames_ocupacionais_vencidos": int(exames_vencidos),
            "treinamentos_vencidos": int(treinamentos_vencidos),
            "epis_pendentes": int(epis_pendentes),
            "custo_estimado_horas_extras": horas_extras * 25.0,
            "absenteismo_operacional": absenteismo_ponto,
        },
        "graficos": {
            "headcount_por_departamento": headcount_por_departamento,
            "admissoes_desligamentos_mes": movimentos,
            "afastamentos_por_tipo": afastamentos_tipo,
            "ferias_por_status": ferias_status,
            "custo_por_rubrica": custo_por_rubrica,
            "custo_por_departamento": custo_por_departamento,
            "horas_extras_por_departamento": [
                {"departamento": departamentos_map.get(item["departamento_id"], "Sem departamento"), "valor": item["horas_extras"]}
                for item in resumo_ponto_departamento(db)
            ],
            "inconsistencias_ponto_mes": ponto_por_mes,
            "banco_horas_por_departamento": [
                {"departamento": departamentos_map.get(dept_id, "Sem departamento"), "saldo": saldo}
                for dept_id, saldo in banco_por_departamento.items()
            ],
            "documentos_vencidos_por_tipo": documentos_por_tipo,
            "exames_vencidos_por_tipo": exames_por_tipo,
            "alertas_por_severidade": alertas_severidade,
            "absenteismo_por_origem": [
                {"origem": "afastamentos", "valor": afastamentos_em_dias(db, competencia)},
                {"origem": "faltas_ponto", "valor": horas_faltantes},
            ],
        },
    }


def list_records_like_ferias(db: Session) -> list[Ferias]:
    return list(db.scalars(select(Ferias).where(Ferias.deletado_em.is_(None))).all())


def _match_colaborador(colaboradores: list[Colaborador], colaborador_id: int) -> bool:
    return any(item.id == colaborador_id for item in colaboradores)


def resumo_ponto_departamento(db: Session) -> list[dict]:
    rows = db.execute(
        select(
            Colaborador.departamento_id,
            func.coalesce(func.sum(ApuracaoPonto.horas_extras), 0),
        )
        .join(Colaborador, Colaborador.id == ApuracaoPonto.colaborador_id)
        .group_by(Colaborador.departamento_id)
    ).all()
    return [{"departamento_id": departamento_id, "horas_extras": float(horas_extras or 0)} for departamento_id, horas_extras in rows]
