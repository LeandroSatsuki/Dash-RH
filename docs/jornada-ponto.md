# Jornada e Ponto Operacional

## Objetivo

Controlar jornada, marcacoes, apuracao e ajustes de ponto como apoio operacional ao DP e a folha.

## Telas

- `15_jornadas.py`
- `16_ponto.py`
- `17_banco_horas.py`

## Permissoes

- `jornadas:view`, `jornadas:create`, `jornadas:update`
- `ponto:view`, `ponto:create`, `ponto:update`, `ponto:approve`
- `banco_horas:view`, `banco_horas:update`

## Regras

- Um colaborador pode ter apenas uma jornada ativa na mesma data.
- Turno de descanso nao exige horarios.
- Marcacao manual registra auditoria.
- Ajuste de ponto exige motivo.
- Competencia de folha continua separada do ponto.
- Banco de horas usa configuracao de saldo negativo.

## Auditoria

- Vinculo de jornada
- Marcacao manual
- Aprovacao e reprovacao de ajuste
- Movimentos manuais de banco de horas

## Limitacoes

- O modulo e operacional interno.
- Nao e certificado como REP.
- Nao substitui validacao juridica ou trabalhista.
- Importacoes devem ser conferidas pelo DP antes de uso operacional.
