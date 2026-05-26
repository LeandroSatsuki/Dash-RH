from __future__ import annotations


def mask_cpf(value: str | None) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if len(digits) != 11:
        return ""
    return f"***.***.***-{digits[-2:]}"


def mask_cnpj(value: str | None) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if len(digits) != 14:
        return ""
    return f"**.***.***/****-{digits[-2:]}"


def mask_email(value: str | None) -> str:
    if not value or "@" not in value:
        return ""
    local, domain = value.split("@", 1)
    if len(local) <= 2:
        return f"{local[0]}***@{domain}"
    return f"{local[:2]}***@{domain}"


def mask_phone(value: str | None) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if len(digits) < 4:
        return ""
    return f"{'*' * max(0, len(digits) - 4)}{digits[-4:]}"


def mask_bank_account(value: str | None) -> str:
    if not value:
        return ""
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if len(digits) < 3:
        return "***"
    return f"{'*' * (len(digits) - 3)}{digits[-3:]}"
