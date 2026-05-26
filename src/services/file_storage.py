from __future__ import annotations

import hashlib
import os
import secrets
from pathlib import Path

from src.utils.config import get_upload_dir

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".xlsx"}
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))


def get_safe_upload_dir() -> Path:
    path = Path(get_upload_dir()).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Extensão de arquivo não permitida.")
    return ext


def validate_size(content: bytes) -> None:
    if len(content) > MAX_UPLOAD_SIZE:
        raise ValueError("Arquivo excede o tamanho máximo permitido.")


def ensure_within_upload_dir(path: str | Path) -> Path:
    upload_dir = get_safe_upload_dir()
    candidate = Path(path).resolve()
    if upload_dir != candidate and upload_dir not in candidate.parents:
        raise ValueError("Documento não pode ser salvo fora da pasta UPLOAD_DIR.")
    return candidate


def generate_internal_name(original_name: str) -> str:
    ext = validate_extension(original_name)
    return f"{secrets.token_hex(16)}{ext}"


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def save_upload(original_name: str, content: bytes) -> dict[str, str]:
    validate_extension(original_name)
    validate_size(content)
    upload_dir = get_safe_upload_dir()
    internal_name = generate_internal_name(original_name)
    destination = ensure_within_upload_dir(upload_dir / internal_name)
    destination.write_bytes(content)
    return {
        "nome_original": original_name,
        "nome_armazenado": internal_name,
        "caminho_arquivo": str(destination),
        "hash_arquivo": sha256_bytes(content),
    }
