# Workflows e Aprovacoes

## Objetivo

Centralizar aprovacoes, reprovacoes, devolucoes e trilha de decisao dos modulos operacionais.

## Telas

- `21_tarefas.py`
- integracoes nas paginas de ferias, ponto, folha, desligamento e documentos

## Permissoes

- `workflows:view`
- `workflows:create`
- `workflows:update`
- `workflows:approve`

## Regras

- toda instancia precisa de entidade vinculada
- reprovacao e devolucao exigem comentario
- comentario passa por sanitizacao
- workflow concluido nao deve ser alterado sem reabertura controlada

## Auditoria

- solicitacao
- aprovacao
- reprovacao
- devolucao
- cancelamento
- alteracao de responsavel

## Limitacoes

- os fluxos foram integrados como camada transversal progressiva
- algumas regras de bloqueio seguem opt-in por configuracao
