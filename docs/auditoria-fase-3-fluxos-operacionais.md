# Auditoria Fase 3 - Fluxos Operacionais

## Estado atual do app operacional

O app operacional ja exige login e respeita permissao por modulo. A base de banco, auditoria, mascaramento, qualidade operacional e folha por competencia esta funcional. O ponto principal antes da fase 3 e que varias paginas ainda atuam como formularios simples sobre CRUD, sem estados de processo, sem confirmacoes de negocio e sem historico funcional completo.

## Paginas existentes

- `01_cadastros.py`
- `02_colaboradores.py`
- `03_admissoes.py`
- `04_ferias.py`
- `05_afastamentos.py`
- `06_beneficios.py`
- `07_folha.py`
- `08_desligamentos.py`
- `09_documentos.py`
- `10_indicadores.py`
- `11_qualidade_dados.py`
- `12_configuracoes.py`
- `13_qualidade_operacional.py`
- `14_auditoria.py`

## CRUDs existentes

- departamentos
- cargos
- centros de custo
- colaboradores
- beneficios
- ferias
- afastamentos
- folha
- desligamentos
- documentos
- auditoria

## Modelos existentes

- `Usuario`
- `Empresa`
- `Departamento`
- `Cargo`
- `CentroCusto`
- `Colaborador`
- `HistoricoFuncional`
- `Admissao`
- `Ferias`
- `Afastamento`
- `Beneficio`
- `ColaboradorBeneficio`
- `CompetenciaFolha`
- `Rubrica`
- `LancamentoFolha`
- `Desligamento`
- `Documento`
- `Auditoria`
- `Importacao`
- `FolhaSnapshot`

## Rotas API existentes

- `POST /auth/login`
- `GET /auth/me`
- `GET|POST|PUT|DELETE /departamentos`
- `GET|POST|PUT /cargos`
- `GET|POST|PUT /centros-custo`
- `GET|POST|GET{id}|PUT|DELETE /colaboradores`
- `GET|POST /beneficios`
- `POST /beneficios/vinculos`
- `GET|POST|PUT /ferias`
- `GET|POST|PUT /afastamentos`
- `GET|POST|PUT /folha/competencias`
- `POST /folha/competencias/{id}/fechar`
- `POST /folha/competencias/{id}/reabrir`
- `GET|POST|PUT /folha/rubricas`
- `GET|POST|PUT /folha/lancamentos`
- `GET|POST|PUT /documentos`
- `GET /indicadores`

## Permissoes existentes

Perfis mapeados:

- admin
- dp
- rh
- gestor
- financeiro
- diretoria
- auditor
- visualizador

Ja existem restricoes importantes para login, indicadores, documentos, folha e auditoria. Ainda faltam permissoes mais finas para eventos de processo, como concluir admissao, aprovar ferias, encerrar afastamento e concluir desligamento.

## Riscos antes da fase 3

- Admissoes ainda nao formam fluxo operacional real.
- Ferias ainda sao gravadas como registro direto, sem aprovacao, conclusao ou sobreposicao.
- Afastamentos nao alteram estado operacional do colaborador nem controlam retorno.
- Beneficios nao possuem encerramento operacional nem analise de obrigatoriedade.
- Desligamentos hoje mudam status de imediato, sem checklist nem encerramento controlado.
- Historico funcional existe no banco, mas ainda nao esta alimentado de forma sistematica nem exibido como trilha operacional.
- Indicadores operacionais ainda precisam ampliar filtros e visoes agregadas por banco.

## Modulos que ainda sao MVP

- admissoes
- ferias
- afastamentos
- beneficios
- desligamentos
- indicadores operacionais
- historico funcional visivel
- UX de confirmacao e erros amigaveis em acoes criticas

## Modulos que precisam virar fluxo operacional real

- Admissao: pre-cadastro, checklist, validacao, conclusao e ativacao do colaborador.
- Ferias: solicitacao, planejamento, aprovacao, cancelamento, conclusao e alertas.
- Afastamentos: registro, atestado, documento, impacto operacional e retorno.
- Beneficios: vinculo, custo, dependentes, encerramento e pendencias.
- Folha: competencia, lancamentos, importacao, resumo e exportacao segura.
- Desligamento: solicitacao, checklist, conclusao, encerramento de beneficios e historico.
- Historico funcional: consolidar eventos e expor visao ao usuario.
