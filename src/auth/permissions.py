from __future__ import annotations

from fastapi import HTTPException, status


PERMISSIONS = {
    "admin": {"*"},
    "dp": {
        "departamentos:view", "departamentos:create", "departamentos:update", "departamentos:delete",
        "cargos:view", "cargos:create", "cargos:update", "cargos:delete",
        "centros_custo:view", "centros_custo:create", "centros_custo:update", "centros_custo:delete",
        "colaboradores:create", "colaboradores:update", "colaboradores:view",
        "admissoes:create", "admissoes:update", "admissoes:view",
        "ferias:create", "ferias:update", "ferias:view",
        "afastamentos:create", "afastamentos:update", "afastamentos:view",
        "beneficios:create", "beneficios:update", "beneficios:view",
        "folha:create", "folha:update", "folha:view",
        "desligamentos:create", "desligamentos:update", "desligamentos:view",
        "documentos:create", "documentos:update", "documentos:view",
        "jornadas:view", "jornadas:create", "jornadas:update",
        "ponto:view", "ponto:create", "ponto:update", "ponto:approve",
        "banco_horas:view", "banco_horas:update",
        "documentos_obrigatorios:view", "documentos_obrigatorios:update",
        "sst:view", "sst:create", "sst:update",
        "alertas:view", "alertas:update",
        "indicadores:view", "auditoria:view", "qualidade:view",
    },
    "rh": {
        "departamentos:view", "cargos:view", "centros_custo:view",
        "colaboradores:view", "admissoes:view", "ferias:view", "afastamentos:view",
        "documentos:view_limited", "beneficios:view", "indicadores:view", "qualidade:view",
        "jornadas:view", "documentos_obrigatorios:view", "alertas:view", "sst:view",
    },
    "gestor": {
        "colaboradores:view_area", "ferias:create", "ferias:view", "indicadores:view_area", "qualidade:view",
        "ponto:view", "alertas:view", "jornadas:view",
    },
    "financeiro": {
        "centros_custo:view", "centros_custo:create", "centros_custo:update",
        "beneficios:view", "beneficios:costs", "folha:view", "folha:create", "folha:update", "custos:view",
        "banco_horas:view", "indicadores:view",
    },
    "diretoria": {"indicadores:view", "custos:view", "colaboradores:view_masked", "qualidade:view", "alertas:view"},
    "auditor": {"auditoria:view", "logs:view", "colaboradores:view_masked", "documentos:view_limited", "qualidade:view", "alertas:view"},
    "visualizador": {"indicadores:view", "colaboradores:view_masked", "alertas:view"},
}


def _get_profile(user) -> str | None:
    if user is None:
        return None
    if isinstance(user, dict):
        return user.get("perfil")
    return getattr(user, "perfil", None)


def ensure_profile(user, allowed_profiles: set[str] | list[str]) -> None:
    allowed = set(allowed_profiles)
    profile = _get_profile(user)
    if profile not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissao insuficiente.")


def has_permission(profile: str, permission: str) -> bool:
    granted = PERMISSIONS.get(profile, set())
    if "*" in granted or permission in granted:
        return True
    aliases = {
        "colaboradores:view": {"colaboradores:view_masked", "colaboradores:view_area"},
        "documentos:view": {"documentos:view_limited"},
        "indicadores:view": {"indicadores:view_area"},
    }
    return any(alias in granted for alias in aliases.get(permission, set()))


def require_permission(user, permission: str) -> None:
    profile = _get_profile(user)
    if profile is None or not has_permission(profile, permission):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissao insuficiente.")
