from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.crud import folha as crud_folha
from src.db.models import Afastamento, Colaborador, ColaboradorBeneficio, CompetenciaFolha, Documento, Ferias, LancamentoFolha
from src.utils.money import decimal_to_float_for_chart


def _safe_divide(numerator: float | int | None, denominator: float | int | None) -> float:
    if numerator in (None, 0) and denominator in (None, 0):
        return 0.0
    if denominator in (None, 0):
        return 0.0
    return float(numerator or 0) / float(denominator)


def headcount_ativo(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Colaborador).where(Colaborador.deletado_em.is_(None), Colaborador.status == "ativo")) or 0


def headcount_por_area(db: Session) -> list[dict]:
    rows = db.execute(
        select(Colaborador.departamento_id, func.count())
        .where(Colaborador.deletado_em.is_(None), Colaborador.status == "ativo")
        .group_by(Colaborador.departamento_id)
    ).all()
    return [{"departamento_id": row[0], "total": row[1]} for row in rows]


def admissoes_no_mes(db: Session, competencia: str) -> int:
    return db.scalar(select(func.count()).select_from(Colaborador).where(func.strftime("%Y-%m", Colaborador.data_admissao) == competencia)) or 0


def desligamentos_no_mes(db: Session, competencia: str) -> int:
    return db.scalar(select(func.count()).select_from(Colaborador).where(func.strftime("%Y-%m", Colaborador.data_desligamento) == competencia)) or 0


def saldo_headcount(admissoes: int, desligamentos: int) -> int:
    return admissoes - desligamentos


def efetivo_medio(efetivo_inicial: float, efetivo_final: float) -> float:
    return (float(efetivo_inicial or 0) + float(efetivo_final or 0)) / 2


def turnover(admissoes: int, desligamentos: int, efetivo_medio_valor: float) -> float:
    return _safe_divide((admissoes + desligamentos) / 2, efetivo_medio_valor)


def afastamentos_em_dias(db: Session) -> float:
    return float(db.scalar(select(func.coalesce(func.sum(Afastamento.quantidade_dias), 0)).where(Afastamento.deletado_em.is_(None))) or 0)


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


def custo_por_centro_custo(db: Session, competencia_id: int | None = None) -> list[dict]:
    rows = db.execute(
        select(Colaborador.centro_custo_id, func.coalesce(func.sum(LancamentoFolha.valor), 0))
        .join(Colaborador, Colaborador.id == LancamentoFolha.colaborador_id)
        .where(LancamentoFolha.deletado_em.is_(None))
        .group_by(Colaborador.centro_custo_id)
    ).all()
    return [{"centro_custo_id": row[0], "valor": float(row[1] or 0)} for row in rows]


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
    if competencia:
        adm = admissoes_no_mes(db, competencia)
        desl = desligamentos_no_mes(db, competencia)
        competencia_obj = db.scalar(select(CompetenciaFolha).where(CompetenciaFolha.competencia == competencia))
    else:
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
    }
