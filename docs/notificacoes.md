# Notificacoes

## Objetivo

Entregar avisos internos de tarefas, aprovacoes, vencimentos e alertas no proprio app operacional.

## Telas

- `22_notificacoes.py`
- sidebar e Home operacional

## Permissoes

- `notificacoes:view`
- `notificacoes:update`

## Regras

- notificacoes internas sao o padrao
- e-mail e webhook ficam desativados por padrao
- credenciais externas devem vir do ambiente
- mensagens passam por sanitizacao e nao devem carregar dados sensiveis

## Auditoria

- criacao
- leitura
- marcar uma ou todas como lidas
- disparos externos registram tentativa sem expor segredo

## Limitacoes

- nao ha envio real sem configuracao explicita
- o sistema nao envia salario, CPF ou dado medico em notificacao externa
