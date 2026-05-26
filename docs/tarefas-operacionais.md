# Tarefas Operacionais

## Objetivo

Organizar pendencias operacionais com responsavel, prazo, comentarios e anexos.

## Telas

- `21_tarefas.py`
- Home operacional

## Permissoes

- `tarefas:view`
- `tarefas:create`
- `tarefas:update`
- `tarefas:assign`
- `tarefas:comment`

## Regras

- tarefa critica precisa de prazo
- cancelamento exige motivo
- comentario passa por sanitizacao
- tarefas vencidas geram alerta e notificacao

## Auditoria

- criacao
- alteracao de responsavel
- conclusao
- cancelamento
- comentarios e exportacoes relacionadas

## Limitacoes

- anexos reaproveitam documentos existentes
- ainda nao existe fila assíncrona dedicada de processamento
