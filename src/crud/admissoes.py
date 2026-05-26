from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from src.crud.base import create_record, get_record, list_records, update_record
from src.crud import colaboradores as crud_colaboradores
from src.db.models import Admissao, Colaborador
from src.services.audit_service import log_action
from src.services.historico import registrar_historico
from src.services.validacoes_dp import digits_only
from src.utils.money import safe_decimal

CHECKLIST_FIELDS = {
    "cpf",
    "rg",
    "comprovante_residencia",
    "dados_bancarios",
    "ctps_digital",
    "pis_pasep",
    "exame_admissional",
    "contrato_assinado",
    "ficha_registro",
    "termo_beneficios",
}


def _normalize_checklist(checklist: dict | None) -> dict:
    payload = {field: False for field in CHECKLIST_FIELDS}
    payload.update(checklist or {})
    return payload


def _derive_status(checklist: dict, data_admissao: date | None) -> str:
    if not checklist.get("exame_admissional"):
        return "exame_pendente"
    if not checklist.get("contrato_assinado") or not checklist.get("ficha_registro"):
        return "contrato_pendente"
    documentos = CHECKLIST_FIELDS - {"exame_admissional", "contrato_assinado", "ficha_registro"}
    if any(not checklist.get(field) for field in documentos):
        return "documentos_pendentes"
    if data_admissao is None:
        return "rascunho"
    return "pronto_para_admitir"


def _validar_conclusao(colaborador: Colaborador, admissao: Admissao) -> None:
    checklist = _normalize_checklist(admissao.checklist_json)
    if (colaborador.regime_contratual or "").upper() == "CLT" and not digits_only(colaborador.cpf):
        raise ValueError("Nao e possivel concluir admissao CLT sem CPF.")
    if admissao.data_admissao is None:
        raise ValueError("Nao e possivel concluir admissao sem data de admissao.")
    if colaborador.cargo_id is None:
        raise ValueError("Nao e possivel concluir admissao sem cargo.")
    if colaborador.departamento_id is None:
        raise ValueError("Nao e possivel concluir admissao sem departamento.")
    if colaborador.centro_custo_id is None:
        raise ValueError("Nao e possivel concluir admissao sem centro de custo.")
    if (colaborador.regime_contratual or "").upper() == "CLT" and safe_decimal(colaborador.salario_base) is None:
        raise ValueError("Nao e possivel concluir admissao CLT sem salario.")
    if any(not checklist.get(field) for field in CHECKLIST_FIELDS):
        raise ValueError("Nao e possivel concluir admissao com checklist incompleto.")


def criar(db: Session, data: dict, usuario_id: int | None = None):
    payload = data.copy()
    payload["checklist_json"] = _normalize_checklist(payload.get("checklist_json"))
    if payload.get("status") in (None, "rascunho"):
        payload["status"] = _derive_status(payload["checklist_json"], payload.get("data_admissao"))
    return create_record(db, Admissao, payload, usuario_id)


def listar(db: Session):
    return list_records(db, Admissao, include_deleted=True)


def buscar_por_id(db: Session, admissao_id: int):
    return get_record(db, Admissao, admissao_id)


def editar(db: Session, admissao_id: int, data: dict, usuario_id: int | None = None):
    admissao = buscar_por_id(db, admissao_id)
    payload = data.copy()
    checklist = _normalize_checklist(payload.get("checklist_json", admissao.checklist_json))
    payload["checklist_json"] = checklist
    if payload.get("status") in (None, "rascunho", "documentos_pendentes", "exame_pendente", "contrato_pendente", "pronto_para_admitir"):
        payload["status"] = _derive_status(checklist, payload.get("data_admissao", admissao.data_admissao))
    return update_record(db, admissao, payload, usuario_id)


def concluir(db: Session, admissao_id: int, usuario_id: int | None = None):
    admissao = buscar_por_id(db, admissao_id)
    colaborador = db.get(Colaborador, admissao.colaborador_id)
    if colaborador is None:
        raise ValueError("Colaborador vinculado nao encontrado.")
    _validar_conclusao(colaborador, admissao)
    update_record(db, colaborador, {"status": "ativo", "data_admissao": admissao.data_admissao, "data_desligamento": None}, usuario_id)
    admissao = update_record(db, admissao, {"status": "concluida"}, usuario_id)
    registrar_historico(
        db,
        colaborador_id=colaborador.id,
        tipo_evento="admissao",
        data_evento=admissao.data_admissao,
        data_inicio=admissao.data_admissao,
        usuario_id=usuario_id,
        valor_novo="ativo",
        motivo="Conclusao de admissao",
    )
    log_action(db, tabela="admissoes", acao="concluir_admissao", registro_id=admissao.id, usuario_id=usuario_id, origem="admissoes", valor_novo={"colaborador_id": colaborador.id, "status": "concluida"})
    return admissao


def cancelar(db: Session, admissao_id: int, usuario_id: int | None = None, motivo: str | None = None):
    admissao = buscar_por_id(db, admissao_id)
    atualizado = update_record(db, admissao, {"status": "cancelada", "observacao": motivo or admissao.observacao}, usuario_id)
    log_action(db, tabela="admissoes", acao="cancelar_admissao", registro_id=atualizado.id, usuario_id=usuario_id, origem="admissoes", valor_novo={"status": "cancelada"})
    return atualizado


def criar_pre_admissao(db: Session, colaborador_data: dict, admissao_data: dict, usuario_id: int | None = None):
    colaborador_payload = {**colaborador_data, "status": "pre_admissao", "origem": colaborador_data.get("origem", "manual")}
    colaborador = crud_colaboradores.criar(db, colaborador_payload, usuario_id)
    admissao_payload = {
        "colaborador_id": colaborador.id,
        "data_prevista_admissao": admissao_data.get("data_prevista_admissao"),
        "data_admissao": admissao_data.get("data_admissao"),
        "checklist_json": admissao_data.get("checklist_json"),
        "observacao": admissao_data.get("observacao"),
    }
    admissao = criar(db, admissao_payload, usuario_id)
    return colaborador, admissao
