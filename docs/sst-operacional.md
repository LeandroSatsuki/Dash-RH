# SST Operacional Base

## Objetivo

Controlar exames ocupacionais, EPI, treinamentos e vencimentos operacionais de SST.

## Telas

- `19_sst.py`
- `20_alertas.py`

## Permissoes

- `sst:view`, `sst:create`, `sst:update`
- `alertas:view`, `alertas:update`

## Regras

- Exame vencido gera qualidade e alerta.
- EPI com CA vencido gera alerta.
- Treinamento vencido gera qualidade e alerta.
- Documento medico e dado sensivel protegido por mascaramento e auditoria.
- Nao existe transmissao oficial para eSocial.

## Auditoria

- Cadastro de exame
- Cadastro e entrega de EPI
- Cadastro e vinculo de treinamento
- Visualizacao sensivel via servico central

## Limitacoes

- O modulo e base operacional de SST.
- Nao substitui software especializado ou consultoria legal.
