# Documentos Obrigatorios

## Objetivo

Definir matriz de obrigatoriedade documental por regime, cargo e departamento, gerar pendencias e acompanhar vencimentos.

## Telas

- `09_documentos.py`
- `18_documentos_obrigatorios.py`

## Permissoes

- `documentos:view`, `documentos:update`
- `documentos_obrigatorios:view`, `documentos_obrigatorios:update`

## Regras

- Regras podem considerar regime contratual, cargo e departamento.
- Pendencias podem ser aprovadas ou dispensadas com justificativa.
- Documento vencido entra em qualidade operacional e alertas.
- Upload continua usando storage seguro.

## Auditoria

- Criacao de tipo
- Criacao de regra
- Geracao de pendencias
- Aprovacao e dispensa
- Visualizacao de dados sensiveis segue auditoria central

## Limitacoes

- O modulo organiza controle interno e pendencias.
- Nao substitui analise legal do conjunto documental obrigatorio da empresa.
