# Mapeamento Inicial para eSocial

O sistema gera apenas preparação, validação e prévias internas. Não realiza envio oficial automático ao eSocial.

## Eventos

### S-2190
- Finalidade: admissão preliminar
- Campos internos usados: `nome_completo`, `cpf`, `data_admissao`
- Campos pendentes: dependem do cadastro completo
- Limitações: sem transmissão oficial

### S-2200
- Finalidade: admissão/vínculo
- Campos internos usados: `nome_completo`, `cpf`, `data_admissao`, `cargo_id`, `departamento_id`
- Campos pendentes: lotação tributária, categoria eSocial, jornada detalhada
- Limitações: sem transmissão oficial

### S-2205
- Finalidade: alteração cadastral
- Campos internos usados: `nome_completo`, `nome_social`, `email`, `telefone`, `endereco`
- Campos pendentes: alguns dados civis ainda não modelados
- Limitações: sem transmissão oficial

### S-2206
- Finalidade: alteração contratual
- Campos internos usados: `cargo_id`, `departamento_id`, `salario_base`, `jornada_semanal`
- Campos pendentes: dados completos de contrato e motivo da alteração
- Limitações: sem transmissão oficial

### S-2230
- Finalidade: afastamento temporário
- Campos internos usados: dados de afastamento vinculados ao colaborador
- Campos pendentes: motivo detalhado no padrão eSocial
- Limitações: sem transmissão oficial

### S-2299
- Finalidade: desligamento
- Campos internos usados: `data_desligamento`, `status`
- Campos pendentes: verbas rescisórias detalhadas
- Limitações: sem transmissão oficial

### S-1200
- Finalidade: remuneração
- Campos internos usados: lançamentos de folha e salário base
- Campos pendentes: mapeamento completo por rubrica
- Limitações: sem transmissão oficial

### S-1210
- Finalidade: pagamentos
- Campos internos usados: lançamentos financeiros da folha
- Campos pendentes: integração bancária e pagamentos efetivos
- Limitações: sem transmissão oficial

### S-1299
- Finalidade: fechamento
- Campos internos usados: status da competência
- Campos pendentes: conferências fiscais completas
- Limitações: sem transmissão oficial

### S-2210
- Finalidade: CAT
- Campos internos usados: afastamentos relacionados
- Campos pendentes: detalhes do acidente
- Limitações: sem transmissão oficial

### S-2220
- Finalidade: monitoramento de saúde
- Campos internos usados: documentos e status do colaborador
- Campos pendentes: ASO e exames ocupacionais completos
- Limitações: sem transmissão oficial

### S-2240
- Finalidade: condições ambientais
- Campos internos usados: cargo e departamento
- Campos pendentes: agentes nocivos, LTCAT e laudos
- Limitações: sem transmissão oficial
