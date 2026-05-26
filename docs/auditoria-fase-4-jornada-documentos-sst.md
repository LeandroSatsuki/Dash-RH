# Auditoria Fase 4 - Jornada, Documentos e SST

## Estado atual dos modelos

O projeto ja possui base transacional para:

- colaboradores
- admissoes
- ferias
- afastamentos
- beneficios
- folha
- desligamentos
- documentos
- importacoes
- auditoria
- historico funcional

Ainda nao existem tabelas especificas para:

- jornada e escala
- ponto e apuracao
- banco de horas
- tipos de documentos obrigatorios e pendencias
- SST ocupacional
- alertas operacionais

## Estado atual das paginas operacionais

Paginas existentes:

- Home
- Cadastros
- Colaboradores
- Admissoes
- Ferias
- Afastamentos
- Beneficios
- Folha
- Desligamentos
- Documentos
- Indicadores
- Qualidade de dados
- Configuracoes
- Qualidade Operacional
- Auditoria

Gaps:

- nao ha tela de jornada/escala
- nao ha tela de ponto
- nao ha tela de banco de horas
- nao ha tela de documentos obrigatorios
- nao ha tela de SST
- nao ha tela dedicada de alertas

## Rotas API existentes

Rotas atuais cobrem:

- auth
- departamentos
- cargos
- centros de custo
- colaboradores
- admissoes
- beneficios
- ferias
- afastamentos
- folha
- desligamentos
- documentos
- indicadores

Nao existem rotas para:

- jornadas
- ponto
- banco de horas
- documentos obrigatorios
- SST
- alertas

## Permissoes existentes

Perfis:

- admin
- dp
- rh
- gestor
- financeiro
- diretoria
- auditor
- visualizador

O modelo atual ainda nao possui permissoes finas para:

- jornadas
- ponto
- aprovacao de ajuste
- banco de horas
- documentos obrigatorios
- SST
- alertas operacionais

## Gaps para jornada/ponto

- colaborador nao possui jornada vinculada por historico
- nao ha escala semanal
- nao ha marcacoes de ponto
- nao ha apuracao
- nao ha inconsistencias operacionais de ponto
- nao ha importacao generica de ponto

## Gaps para documentos obrigatorios

- documentos existem, mas sem matriz por regime/cargo/departamento
- nao ha pendencia operacional automatica
- nao ha aprovacao ou dispensa de obrigatoriedade
- nao ha severidade de pendencia documental

## Gaps para SST

- nao ha controle de exame ocupacional
- nao ha cadastro de EPI
- nao ha entrega de EPI
- nao ha treinamento SST
- nao ha alertas de vencimento SST

## Riscos de dados sensiveis

- ponto pode embutir jornada e comportamento individual sensivel
- documentos obrigatorios podem incluir itens pessoais e medicos
- SST lida com ASO e dados medicos
- qualquer visualizacao sem mascara precisa manter controle por permissao e auditoria

## Tabelas que precisam ser criadas

- jornadas
- turnos
- colaborador_jornadas
- marcacoes_ponto
- apuracoes_ponto
- ajustes_ponto
- banco_horas_movimentos
- configuracoes_sistema
- tipos_documento
- documentos_obrigatorios_regras
- documentos_pendencias
- exames_ocupacionais
- epis
- entregas_epi
- treinamentos_sst
- colaborador_treinamentos_sst
- alertas

## Modulos reaproveitaveis

- `audit_service.py` para trilha de auditoria
- `file_storage.py` para anexos e documentos
- `historico.py` para eventos funcionais
- `data_quality.py` para consolidar novos problemas
- `indicadores.py` para ampliar agregacoes operacionais
- `seed_demo.py` para gerar dados ficticios
