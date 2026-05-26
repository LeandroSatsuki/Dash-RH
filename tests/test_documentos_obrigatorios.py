from datetime import date, timedelta

from src.crud import colaboradores as crud_colaboradores
from src.crud import documentos_obrigatorios as crud_docs
from src.db.models import Documento


def _colaborador(db):
    return crud_colaboradores.criar(
        db,
        {"nome_completo": "Docs Demo", "cpf": "90000000035", "regime_contratual": "CLT", "status": "ativo", "salario_base": 2000},
        1,
    )


def test_gera_pendencia_por_regime(db):
    colaborador = _colaborador(db)
    tipo = crud_docs.criar_tipo_documento(db, {"nome": "rg", "sensivel": False, "exige_validade": False, "ativo": True}, 1)
    crud_docs.criar_regra(db, {"tipo_documento_id": tipo.id, "regime_contratual": "CLT", "obrigatorio": True}, 1)
    pendencias = crud_docs.gerar_pendencias(db, 1)
    assert len(pendencias) == 1
    assert pendencias[0].colaborador_id == colaborador.id


def test_pendencia_vira_vencida_quando_documento_vence(db):
    colaborador = _colaborador(db)
    tipo = crud_docs.criar_tipo_documento(db, {"nome": "aso", "sensivel": True, "exige_validade": True, "ativo": True}, 1)
    crud_docs.criar_regra(db, {"tipo_documento_id": tipo.id, "regime_contratual": "CLT", "obrigatorio": True}, 1)
    pendencia = crud_docs.gerar_pendencias(db, 1)[0]
    db.add(
        Documento(
            colaborador_id=colaborador.id,
            tipo_documento="aso",
            nome_original="aso.pdf",
            nome_armazenado="aso.pdf",
            caminho_arquivo="data/uploads/aso.pdf",
            hash_arquivo="hash-demo",
            validade=date.today() - timedelta(days=1),
            status="ativo",
            usuario_upload_id=1,
        )
    )
    db.commit()
    crud_docs.gerar_pendencias(db, 1)
    atualizada = db.get(type(pendencia), pendencia.id)
    assert atualizada.status == "vencido"


def test_dispensar_exige_justificativa(db):
    _colaborador(db)
    tipo = crud_docs.criar_tipo_documento(db, {"nome": "ctps", "ativo": True}, 1)
    crud_docs.criar_regra(db, {"tipo_documento_id": tipo.id, "regime_contratual": "CLT", "obrigatorio": True}, 1)
    pendencia = crud_docs.gerar_pendencias(db, 1)[0]
    try:
        crud_docs.dispensar_pendencia(db, pendencia.id, "", 1)
        assert False, "Esperava exigencia de justificativa."
    except ValueError as exc:
        assert "justificativa" in str(exc)
