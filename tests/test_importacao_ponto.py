from pathlib import Path

from src.crud import colaboradores as crud_colaboradores
from src.services.importacao_ponto import importar_marcacoes


def test_importacao_ponto_por_matricula(db, tmp_path: Path):
    crud_colaboradores.criar(
        db,
        {"nome_completo": "Import Demo", "matricula": "MAT001", "cpf": "90000000040", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000},
        1,
    )
    arquivo = tmp_path / "ponto.csv"
    arquivo.write_text("matricula,data,entrada,saida\nMAT001,2026-01-10,08:00,17:00\n", encoding="utf-8")
    resultado = importar_marcacoes(
        db,
        path=arquivo,
        column_map={"matricula": "matricula", "data": "data", "entrada": "entrada", "saida": "saida"},
        usuario_id=1,
    )
    assert resultado.importadas == 1
    assert resultado.erros == []


def test_importacao_ponto_reporta_duplicidade(db, tmp_path: Path):
    crud_colaboradores.criar(
        db,
        {"nome_completo": "Import Duplicado", "matricula": "MAT002", "cpf": "90000000041", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000},
        1,
    )
    arquivo = tmp_path / "ponto_dup.csv"
    arquivo.write_text("matricula,data,entrada,saida\nMAT002,2026-01-10,08:00,17:00\nMAT002,2026-01-10,08:00,17:00\n", encoding="utf-8")
    resultado = importar_marcacoes(
        db,
        path=arquivo,
        column_map={"matricula": "matricula", "data": "data", "entrada": "entrada", "saida": "saida"},
        usuario_id=1,
    )
    assert resultado.importadas == 1
    assert len(resultado.erros) == 1
