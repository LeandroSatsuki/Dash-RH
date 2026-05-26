# Alertas Operacionais

## Objetivo

Centralizar vencimentos, inconsistencias e pendencias operacionais em uma fila unica de acompanhamento.

## Telas

- `20_alertas.py`
- Home operacional

## Permissoes

- `alertas:view`
- `alertas:update`

## Regras

- Alertas podem ser gerados automaticamente a partir de documentos, ponto, SST, ferias, folha e qualidade.
- Alerta pode ser resolvido ou ignorado com justificativa.
- Dados sensiveis nao sao expostos no payload de exportacao ou listagem.

## Auditoria

- Geracao de alertas
- Resolucao
- Ignorar com justificativa

## Limitacoes

- Os alertas sao apoio operacional e nao substituem esteiras formais de compliance.
