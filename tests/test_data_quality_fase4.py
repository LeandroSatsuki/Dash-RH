from datetime import date, timedelta

from src.crud import colaboradores as crud_colaboradores
from src.crud import documentos_obrigatorios as crud_docs
from src.crud import sst as crud_sst
from src.services.data_quality import generate_operational_quality_report


def test_quality_fase4_detecta_sem_jornada_e_documento_pendente(db):
    crud_colaboradores.criar(
        db,
        {"nome_completo": "Qualidade F4", "cpf": "90000000043", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000},
        1,
    )
    tipo = crud_docs.criar_tipo_documento(db, {"nome": "rg_f4", "ativo": True}, 1)
    crud_docs.criar_regra(db, {"tipo_documento_id": tipo.id, "regime_contratual": "CLT", "obrigatorio": True}, 1)
    crud_docs.gerar_pendencias(db, 1)
    issues = generate_operational_quality_report(db)
    tipos = {item["tipo"] for item in issues}
    assert "Colaborador ativo sem jornada" in tipos
    assert "Documento obrigatorio pendente" in tipos


def test_quality_fase4_detecta_epi_e_exame_vencidos(db):
    colaborador = crud_colaboradores.criar(
        db,
        {"nome_completo": "Qualidade SST", "cpf": "90000000044", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000},
        1,
    )
    crud_sst.criar_exame(db, {"colaborador_id": colaborador.id, "tipo_exame": "periodico", "data_exame": date.today() - timedelta(days=365), "data_validade": date.today() - timedelta(days=1), "status": "ativo"}, 1)
    crud_sst.criar_epi(db, {"nome": "Capacete", "ca": "CA123", "validade_ca": date.today() - timedelta(days=1), "ativo": True}, 1)
    issues = generate_operational_quality_report(db)
    tipos = {item["tipo"] for item in issues}
    assert "Exame ocupacional vencido" in tipos
    assert "EPI com CA vencido" in tipos
