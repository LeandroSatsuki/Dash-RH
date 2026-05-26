# Relatorios Operacionais

## Objetivo

Permitir exportacoes operacionais sem expor dados sensiveis por padrao.

## Telas

- `24_relatorios_operacionais.py`

## Permissoes

- `relatorios_operacionais:view`
- `relatorios_operacionais:export`

## Regras

- exporta em CSV e XLSX
- CPF deve permanecer mascarado
- salario individual so deve sair para perfis autorizados
- dado medico nao sai em relatorio geral

## Auditoria

- cada exportacao registra evento na auditoria central

## Limitacoes

- os arquivos sao gerados sob demanda e nao devem ser persistidos em pasta versionada
