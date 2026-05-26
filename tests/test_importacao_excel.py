from src.crud import colaboradores as crud_colaboradores
from src.services import importacao_excel


def test_importacao_nao_duplica_colaborador(db, monkeypatch, tmp_path):
    fake_rows = [
        {"ID_Colaborador": "1", "Nome_RazaoSocial": "Pessoa A", "CPF": "12345678901", "Regime_Contratual": "CLT", "Data_Admissao": None, "Data_Desligamento": None},
        {"ID_Colaborador": "1", "Nome_RazaoSocial": "Pessoa A", "CPF": "12345678901", "Regime_Contratual": "CLT", "Data_Admissao": None, "Data_Desligamento": None},
    ]

    monkeypatch.setattr(importacao_excel, "worksheet_to_table", lambda *args, **kwargs: fake_rows)
    arquivo = tmp_path / "fake.xlsx"
    arquivo.write_text("fake")
    resultado = importacao_excel.importar_colaboradores_cadastro(db, arquivo, 1)
    itens = crud_colaboradores.listar(db)
    assert resultado["linhas_importadas"] == 1
    assert len(itens) == 1
