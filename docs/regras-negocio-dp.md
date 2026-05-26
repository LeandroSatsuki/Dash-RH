# Regras de Negócio DP

## Admissão
- CPF é obrigatório para CLT.
- Novos registros devem nascer preferencialmente do banco, não da planilha.

## Férias
- Data final não pode ser menor que data inicial.
- Férias vencidas devem aparecer em alertas.

## Afastamentos
- Data final não pode ser menor que data inicial.
- Deve haver indicação de impacto em folha e absenteísmo.

## Folha
- Competência fechada não recebe novos lançamentos sem reabertura.
- Valor negativo só é aceito para desconto quando a regra permitir.

## Desligamento
- Colaborador desligado deve ter data de desligamento.
- Colaborador ativo não deve manter data de desligamento.

## Benefícios
- Benefícios podem ser vinculados por colaborador.
- Custos empresa e colaborador ficam separados.

## Documentos
- Documento só pode ser salvo dentro de `UPLOAD_DIR`.
- Deve haver validade e status para controle operacional.

## Qualidade de dados
- Monitorar CPF ausente, salário ausente, cargo ausente, departamento ausente e inconsistências de status.
