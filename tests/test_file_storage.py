from pathlib import Path

from src.services.file_storage import ensure_within_upload_dir, save_upload


def test_file_storage_salva_no_upload_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    result = save_upload("arquivo.pdf", b"conteudo")
    assert Path(result["caminho_arquivo"]).exists()
    assert Path(result["caminho_arquivo"]).parent == tmp_path.resolve()


def test_file_storage_bloqueia_path_escape(monkeypatch, tmp_path):
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))
    try:
        ensure_within_upload_dir(tmp_path.parent / "fora.pdf")
        assert False, "Era esperado bloqueio"
    except ValueError:
        assert True
