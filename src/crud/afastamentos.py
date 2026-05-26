from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, soft_delete_record, update_record
from src.db.models import Afastamento, Colaborador, Documento
from src.services.audit_service import log_action
from src.services.file_storage import save_upload
from src.services.historico import registrar_historico
from src.services.validacoes_dp import validar_periodo

STATUS_AFETADOS = {"atestado_medico", "licenca_maternidade", "licenca_paternidade", "inss", "acidente_trabalho", "licenca_nao_remunerada"}


def _validar(data: dict) -> None:
    validar_periodo(data.get("data_inicio"), data.get("data_fim"), "Afastamento")


def _ajustar_status_colaborador(db: Session, colaborador_id: int, tipo: str, status_afastamento: str) -> None:
    colaborador = db.get(Colaborador, colaborador_id)
    if colaborador is None:
        return
    if status_afastamento == "encerrado" and colaborador.status == "afastado":
        colaborador.status = "ativo"
    elif tipo in STATUS_AFETADOS and status_afastamento == "ativo":
        colaborador.status = "afastado"
    db.add(colaborador)
    db.commit()


def criar(db: Session, data: dict, usuario_id: int | None = None):
    payload = data.copy()
    _validar(payload)
    if payload.get("quantidade_dias") is None and payload.get("data_inicio") and payload.get("data_fim"):
        payload["quantidade_dias"] = float((payload["data_fim"] - payload["data_inicio"]).days + 1)
    afastamento = create_record(db, Afastamento, payload, usuario_id)
    _ajustar_status_colaborador(db, afastamento.colaborador_id, afastamento.tipo, afastamento.status)
    registrar_historico(
        db,
        colaborador_id=afastamento.colaborador_id,
        tipo_evento="afastamento",
        data_evento=afastamento.data_inicio,
        data_inicio=afastamento.data_inicio,
        data_fim=afastamento.data_fim,
        usuario_id=usuario_id,
        motivo=afastamento.tipo,
    )
    return afastamento


def listar(db: Session):
    return list_records(db, Afastamento)


def buscar_por_id(db: Session, afastamento_id: int):
    return get_record(db, Afastamento, afastamento_id)


def editar(db: Session, afastamento_id: int, data: dict, usuario_id: int | None = None):
    obj = buscar_por_id(db, afastamento_id)
    payload = {**obj.__dict__, **data}
    _validar(payload)
    if payload.get("quantidade_dias") is None and payload.get("data_inicio") and payload.get("data_fim"):
        data["quantidade_dias"] = float((payload["data_fim"] - payload["data_inicio"]).days + 1)
    updated = update_record(db, obj, data, usuario_id)
    _ajustar_status_colaborador(db, updated.colaborador_id, updated.tipo, updated.status)
    return updated


def encerrar(db: Session, afastamento_id: int, data_fim: date, usuario_id: int | None = None):
    obj = buscar_por_id(db, afastamento_id)
    if data_fim < obj.data_inicio:
        raise ValueError("Afastamento: data final nao pode ser menor que data inicial.")
    payload = {
        "data_fim": data_fim,
        "status": "encerrado",
        "quantidade_dias": float((data_fim - obj.data_inicio).days + 1),
    }
    updated = update_record(db, obj, payload, usuario_id)
    _ajustar_status_colaborador(db, updated.colaborador_id, updated.tipo, updated.status)
    registrar_historico(
        db,
        colaborador_id=updated.colaborador_id,
        tipo_evento="retorno_afastamento",
        data_evento=data_fim,
        data_inicio=obj.data_inicio,
        data_fim=data_fim,
        usuario_id=usuario_id,
        motivo=updated.tipo,
    )
    log_action(db, tabela="afastamentos", acao="encerrar_afastamento", registro_id=updated.id, usuario_id=usuario_id, origem="afastamentos")
    return updated


def anexar_documento(
    db: Session,
    *,
    afastamento_id: int,
    original_name: str,
    content: bytes,
    usuario_id: int | None = None,
) -> Documento:
    afastamento = buscar_por_id(db, afastamento_id)
    saved = save_upload(original_name, content)
    documento = Documento(
        colaborador_id=afastamento.colaborador_id,
        tipo_documento="atestado_medico" if afastamento.tipo == "atestado_medico" else "documento_afastamento",
        nome_original=saved["nome_original"],
        nome_armazenado=saved["nome_armazenado"],
        caminho_arquivo=saved["caminho_arquivo"],
        hash_arquivo=saved["hash_arquivo"],
        status="ativo",
        usuario_upload_id=usuario_id,
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)
    log_action(db, tabela="documentos", acao="upload_documento_afastamento", registro_id=documento.id, usuario_id=usuario_id, origem="afastamentos", valor_novo={"afastamento_id": afastamento_id})
    return documento


def remover(db: Session, afastamento_id: int, usuario_id: int | None = None):
    return soft_delete_record(db, buscar_por_id(db, afastamento_id), usuario_id)
