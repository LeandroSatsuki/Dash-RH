# Calendario Operacional

## Objetivo

Exibir numa fila temporal unica os principais eventos operacionais de RH/DP.

## Telas

- `23_calendario_operacional.py`

## Permissoes

- `calendario:view`

## Regras

- agrega ferias, afastamentos, vencimentos, tarefas, folha, admissoes e desligamentos
- nao mostra CPF, salario ou dado medico
- filtra por tipo de evento

## Auditoria

- leitura segue auditoria central quando houver dado sensivel vinculado

## Limitacoes

- a visualizacao atual e simples e baseada em lista
- nao ha agenda com sincronizacao externa
