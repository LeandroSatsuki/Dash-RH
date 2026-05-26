from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Session

from src.crud import tarefas as crud_tarefas
from src.db.models import Admissao, Afastamento, ColaboradorTreinamentoSST, CompetenciaFolha, Desligamento, DocumentoPendencia, ExameOcupacional, Ferias


def build_calendar_events(db: Session) -> list[dict]:
    events: list[dict] = []
    for item in db.query(Ferias).all():
        if item.data_inicio:
            events.append({"tipo": "ferias", "data": item.data_inicio, "titulo": f"Ferias colaborador {item.colaborador_id}", "entidade_tipo": "ferias", "entidade_id": item.id})
    for item in db.query(Afastamento).all():
        events.append({"tipo": "afastamento", "data": item.data_inicio, "titulo": f"Afastamento colaborador {item.colaborador_id}", "entidade_tipo": "afastamento", "entidade_id": item.id})
    for item in db.query(DocumentoPendencia).all():
        if item.data_vencimento:
            events.append({"tipo": "documento", "data": item.data_vencimento, "titulo": f"Documento colaborador {item.colaborador_id}", "entidade_tipo": "documento_pendencia", "entidade_id": item.id})
    for item in db.query(ExameOcupacional).all():
        if item.data_validade:
            events.append({"tipo": "exame", "data": item.data_validade, "titulo": f"Exame colaborador {item.colaborador_id}", "entidade_tipo": "exame_ocupacional", "entidade_id": item.id})
    for item in db.query(ColaboradorTreinamentoSST).all():
        if item.data_validade:
            events.append({"tipo": "treinamento", "data": item.data_validade, "titulo": f"Treinamento colaborador {item.colaborador_id}", "entidade_tipo": "colaborador_treinamento_sst", "entidade_id": item.id})
    for item in crud_tarefas.listar(db):
        if item.prazo:
            events.append({"tipo": "tarefa", "data": item.prazo.date(), "titulo": item.titulo, "entidade_tipo": "tarefa", "entidade_id": item.id, "responsavel_id": item.responsavel_id})
    for item in db.query(CompetenciaFolha).all():
        if item.data_abertura:
            events.append({"tipo": "folha", "data": item.data_abertura.date(), "titulo": f"Competencia {item.competencia}", "entidade_tipo": "competencia_folha", "entidade_id": item.id})
    for item in db.query(Desligamento).all():
        if item.data_desligamento:
            events.append({"tipo": "desligamento", "data": item.data_desligamento, "titulo": f"Desligamento colaborador {item.colaborador_id}", "entidade_tipo": "desligamento", "entidade_id": item.id})
    for item in db.query(Admissao).all():
        if item.data_admissao:
            events.append({"tipo": "admissao", "data": item.data_admissao, "titulo": f"Admissao colaborador {item.colaborador_id}", "entidade_tipo": "admissao", "entidade_id": item.id})
    return sorted(events, key=lambda item: item["data"])
