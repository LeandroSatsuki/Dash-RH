from __future__ import annotations

from datetime import date


def digits_only(value: str | None) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def validar_cpf_obrigatorio_clt(regime_contratual: str | None, cpf: str | None) -> None:
    if (regime_contratual or "").upper() == "CLT" and not digits_only(cpf):
        raise ValueError("CPF é obrigatório para colaborador CLT.")


def validar_data_admissao_desligamento(data_admissao: date | None, data_desligamento: date | None) -> None:
    if data_admissao and data_desligamento and data_admissao > data_desligamento:
        raise ValueError("Data de admissão não pode ser maior que data de desligamento.")


def validar_status_colaborador(status: str, data_desligamento: date | None) -> None:
    if status == "ativo" and data_desligamento is not None:
        raise ValueError("Colaborador ativo não deve ter data de desligamento preenchida.")
    if status == "desligado" and data_desligamento is None:
        raise ValueError("Colaborador desligado deve ter data de desligamento preenchida.")


def validar_salario(salario_base: float | None) -> None:
    if salario_base is not None and salario_base < 0:
        raise ValueError("Salário não pode ser negativo.")


def validar_periodo(data_inicio: date | None, data_fim: date | None, descricao: str) -> None:
    if data_inicio and data_fim and data_fim < data_inicio:
        raise ValueError(f"{descricao}: data final não pode ser menor que data inicial.")


def validar_valor_lancamento(valor: float, rubrica_tipo: str | None = None) -> None:
    if valor < 0 and (rubrica_tipo or "") != "desconto":
        raise ValueError("Lançamento de folha não pode ter valor negativo, exceto desconto.")
