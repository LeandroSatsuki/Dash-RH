# Observabilidade e Logs

## Objetivo

Padronizar logs de API e scripts operacionais sem vazar segredos ou dados sensiveis.

## Componentes

- `src/utils/logging_config.py`
- console logging por padrao
- arquivo em `data/logs` quando `LOG_TO_FILE=true`

## Sanitizacao

- CPF e CNPJ mascarados
- salario e valores sensiveis mascarados
- `SECRET_KEY`, tokens, senhas e `SMTP_PASSWORD` redigidos
- URLs sensiveis sem query string

## Uso

- `LOG_LEVEL=INFO|WARNING|ERROR|DEBUG`
- `LOG_TO_FILE=true` para persistencia local controlada

## Limitacoes

- o projeto nao inclui stack externa de observabilidade nesta fase
- integracoes com SIEM ou APM ficam como proximo passo
