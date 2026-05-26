from __future__ import annotations

from src.db.models import Colaborador


ESOCIAL_EVENTS = {
    "S-2190": {"finalidade": "Admissão preliminar", "campos": ["nome_completo", "cpf", "data_admissao"]},
    "S-2200": {"finalidade": "Admissão/vínculo", "campos": ["nome_completo", "cpf", "data_admissao", "cargo_id", "departamento_id"]},
    "S-2205": {"finalidade": "Alteração cadastral", "campos": ["nome_completo", "nome_social", "email", "telefone", "endereco"]},
    "S-2206": {"finalidade": "Alteração contratual", "campos": ["cargo_id", "departamento_id", "salario_base", "jornada_semanal"]},
    "S-2230": {"finalidade": "Afastamento temporário", "campos": ["status"]},
    "S-2299": {"finalidade": "Desligamento", "campos": ["data_desligamento", "status"]},
    "S-1200": {"finalidade": "Remuneração", "campos": ["salario_base"]},
    "S-1210": {"finalidade": "Pagamentos", "campos": ["salario_base"]},
    "S-1299": {"finalidade": "Fechamento", "campos": []},
    "S-2210": {"finalidade": "CAT", "campos": ["status"]},
    "S-2220": {"finalidade": "Monitoramento de saúde", "campos": ["status"]},
    "S-2240": {"finalidade": "Condições ambientais", "campos": ["departamento_id", "cargo_id"]},
}


def gerar_previa_evento(evento: str, colaborador) -> dict:
    config = ESOCIAL_EVENTS[evento]
    campos = {}
    pendencias = []
    for campo in config["campos"]:
        valor = getattr(colaborador, campo, None)
        campos[campo] = valor
        if valor in (None, ""):
            pendencias.append(campo)
    return {
        "evento": evento,
        "finalidade": config["finalidade"],
        "campos": campos,
        "pendencias": pendencias,
        "transmissao_oficial": False,
    }
