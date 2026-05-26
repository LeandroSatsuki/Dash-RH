from datetime import date, timedelta

from src.crud import colaboradores as crud_colaboradores
from src.crud import sst as crud_sst
from src.services.data_quality import generate_operational_quality_report


def _colaborador(db):
    return crud_colaboradores.criar(
        db,
        {"nome_completo": "SST Demo", "cpf": "90000000036", "regime_contratual": "CLT", "status": "ativo", "salario_base": 2000},
        1,
    )


def test_cria_exame_ocupacional(db):
    colaborador = _colaborador(db)
    exame = crud_sst.criar_exame(db, {"colaborador_id": colaborador.id, "tipo_exame": "periodico", "data_exame": date.today(), "data_validade": date.today() + timedelta(days=365), "status": "ativo"}, 1)
    assert exame.id is not None


def test_exame_vencido_entra_na_qualidade(db):
    colaborador = _colaborador(db)
    crud_sst.criar_exame(db, {"colaborador_id": colaborador.id, "tipo_exame": "periodico", "data_exame": date.today() - timedelta(days=365), "data_validade": date.today() - timedelta(days=1), "status": "ativo"}, 1)
    issues = generate_operational_quality_report(db)
    assert any(item["tipo"] == "Exame ocupacional vencido" for item in issues)


def test_treinamento_vencido_entra_na_qualidade(db):
    colaborador = _colaborador(db)
    treinamento = crud_sst.criar_treinamento(db, {"nome": "NR Demo", "validade_meses": 12, "ativo": True}, 1)
    crud_sst.vincular_treinamento(db, {"colaborador_id": colaborador.id, "treinamento_id": treinamento.id, "data_realizacao": date.today() - timedelta(days=400), "data_validade": date.today() - timedelta(days=1), "status": "ativo"}, 1)
    issues = generate_operational_quality_report(db)
    assert any(item["tipo"] == "Treinamento vencido" for item in issues)
