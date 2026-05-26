# Auditoria Fase 5 - Workflows, Aprovacoes, Tarefas e Notificacoes

## Estado atual

O projeto ja possui base operacional transacional com:

- autenticacao obrigatoria no app Streamlit
- API FastAPI autenticada
- auditoria central sanitizada
- permissoes por perfil
- alertas, jornada, ponto, banco de horas, documentos obrigatorios e SST
- indicadores operacionais e qualidade operacional no banco

## Modulos que precisam de aprovacao

- ferias: aprovacao, reprovacao e cancelamento com motivo
- ponto: ajuste manual com aprovacao
- banco de horas: ajuste manual pode exigir aprovacao
- folha: fechamento e reabertura podem exigir fluxo
- desligamento: aprovacao antes da conclusao
- documentos obrigatorios: dispensa com justificativa/aprovacao
- SST: tarefas para vencimentos e tratamento operacional

## Modulos que precisam de tarefas

- documentos vencidos e pendentes
- exames ocupacionais vencidos
- treinamentos vencidos
- ferias vencidas ou a vencer
- ponto inconsistente
- competencias antigas abertas
- desligamentos e admissoes com pendencias

## Modulos que precisam de notificacao

- atribuicao de tarefa
- vencimento de tarefa
- aprovacao pendente
- aprovacao concluida ou reprovada
- alerta critico criado
- documento obrigatorio vencido
- exame vencido
- ponto inconsistente
- folha pendente de fechamento

## Permissoes atuais

O projeto ja possui perfis `admin`, `dp`, `rh`, `gestor`, `financeiro`, `diretoria`, `auditor` e `visualizador`, com matriz crescente por dominio funcional. Ainda nao existem permissoes explicitas para:

- workflows
- tarefas
- notificacoes internas
- calendario operacional
- relatorios operacionais exportaveis

## Riscos de seguranca

- comentarios livres podem receber CPF, salario ou dado medico se nao houver sanitizacao
- notificacoes podem vazar informacao sensivel se montadas com payload bruto
- exportacoes operacionais podem expor salario e documento medico sem filtro de perfil
- aprovacoes sem trilha unica podem fragmentar auditoria

## Riscos de dados sensiveis

- comentarios em workflow e tarefas
- mensagens de notificacao
- anexos e documentos vinculados a tarefas
- relatarios exportados

## Pontos onde auditoria ja existe

- CRUD base e varios servicos especializados
- login e falha de login
- marcacao manual, ajuste de ponto, banco de horas
- uploads e visualizacao sensivel
- fechamento e reabertura de folha
- alertas operacionais

## Pontos onde workflow ainda e manual

- paginas operacionais fazem aprovacoes por botoes locais e regras pontuais
- nao existe instancia central de aprovacao por entidade
- nao existe fila unificada de aprovacoes pendentes
- nao existe tarefa operacional central com responsavel/prazo
- nao existe centro unico de notificacoes internas

## Tabelas que precisam ser criadas

- `workflows`
- `workflow_etapas`
- `workflow_instancias`
- `workflow_historico`
- `tarefas`
- `tarefas_comentarios`
- `tarefas_anexos`
- `notificacoes`
- `configuracoes_notificacao`

## Servicos e componentes reaproveitaveis

- `src/services/audit_service.py`
- `src/services/file_storage.py`
- `src/services/alerts.py`
- `src/services/data_quality.py`
- `src/services/indicadores.py`
- `src/auth/permissions.py`
- `operational_app/common.py`

## Recomendacoes

- centralizar aprovacao em `workflow_service`
- centralizar tarefas em `task_service`
- centralizar notificacoes internas em `notification_service`
- manter notificacao externa desativada por padrao
- usar comentarios sanitizados e payload mascarado em auditoria
- gerar tarefas e notificacoes por script idempotente diario antes de background complexo
