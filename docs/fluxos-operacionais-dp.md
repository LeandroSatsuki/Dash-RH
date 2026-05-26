# Fluxos Operacionais DP

## Admissao

- cria pre-admissao
- preenche dados basicos
- valida checklist
- conclui admissao
- ativa colaborador
- grava historico funcional
- gera auditoria

Permissoes: `admissoes:view`, `admissoes:create`, `admissoes:update`

## Ferias

- solicita ou planeja
- aprova
- cancela
- conclui
- gera retorno em historico
- entra na qualidade operacional quando vencida

Permissoes: `ferias:view`, `ferias:create`, `ferias:update`

## Afastamentos

- registra afastamento, falta ou atestado
- calcula dias
- altera status operacional quando aplicavel
- anexa documento com `file_storage`
- encerra retorno
- grava historico e auditoria

Permissoes: `afastamentos:view`, `afastamentos:create`, `afastamentos:update`

## Beneficios

- cadastra beneficio
- vincula ao colaborador
- controla valores empresa e colaborador
- controla dependentes
- encerra vinculo
- apoia custo e pendencias

Permissoes: `beneficios:view`, `beneficios:create`, `beneficios:update`

## Folha

- abre competencia
- lanca rubricas
- fecha competencia
- gera snapshot
- reabre competencia
- exporta resumo da competencia

Permissoes: `folha:view`, `folha:create`, `folha:update`

## Desligamento

- cria solicitacao
- define tipo e datas
- conclui desligamento
- encerra beneficios ativos
- atualiza colaborador
- grava historico funcional e auditoria

Permissoes: `desligamentos:view`, `desligamentos:create`, `desligamentos:update`

## Impacto em indicadores

- admissoes e desligamentos alteram headcount e turnover
- afastamentos impactam absenteismo e status
- ferias impactam pendencias, vencimentos e calendario
- folha fechada alimenta snapshot e custo
- beneficios alimentam custo mensal e pendencias
