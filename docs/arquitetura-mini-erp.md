# Arquitetura Mini ERP RH/DP

## Visao geral

O projeto segue uma arquitetura hibrida:

- `main.py` e `dashboard/app.py` preservam o fluxo legado de planilhas e analises.
- `src/db`, `src/crud`, `src/services`, `src/api` e `operational_app` formam a camada transacional do mini ERP.

## Camadas

- `src/db`: configuracao do banco, sessao, modelos SQLAlchemy, bootstrap e migracoes.
- `src/auth`: hash de senha, autenticacao e matriz de permissoes.
- `src/crud`: operacoes transacionais com soft delete e auditoria central.
- `src/schemas`: contratos Pydantic para API e servicos.
- `src/services`: indicadores, importacao Excel, auditoria, qualidade de dados, mascaramento, valores monetarios e armazenamento de arquivos.
- `src/services`: indicadores, importacao Excel, importacao de ponto, auditoria, alertas, qualidade de dados, mascaramento, valores monetarios e armazenamento de arquivos.
- `src/api`: API FastAPI autenticada por token.
- `operational_app`: interface Streamlit com login real e bloqueio por perfil.
- `dashboard`: dashboard legado independente do banco.

## Fluxo operacional

1. Usuario autentica no app operacional ou API.
2. Permissoes filtram modulos e acoes.
3. CRUD grava dados no banco com soft delete quando aplicavel.
4. Auditoria central registra criacao, edicao, exclusao logica, login, falha de login, fechamento de competencia, reabertura, upload e importacao.
5. Jornada, ponto, banco de horas, documentos obrigatorios, SST e alertas operam no banco principal.
6. Indicadores leem preferencialmente o banco operacional e usam snapshots de folha quando a competencia esta fechada.
7. Pipeline legado continua disponivel para importacao e analise historica.

## Banco de dados

- ORM: SQLAlchemy.
- Desenvolvimento padrao: SQLite via `DATABASE_URL=sqlite:///./data/app/dash_rh.db`.
- Producao recomendada: PostgreSQL via `DATABASE_URL=postgresql+psycopg://...`.
- Campos monetarios usam `Numeric(14, 2)` e `Decimal`.
- Migracoes versionadas usam Alembic.

## Seguranca

- Senhas com hash seguro.
- Login obrigatorio no app operacional.
- Controle de acesso por perfil:
  - `admin`
  - `dp`
  - `rh`
  - `gestor`
  - `financeiro`
  - `diretoria`
  - `auditor`
  - `visualizador`
- Dados sensiveis ficam mascarados por padrao.
- Uploads ficam restritos a `UPLOAD_DIR`, com validacao de extensao, tamanho e path seguro.
- O modulo de ponto e operacional interno e nao declara conformidade legal de REP.

## Auditoria

- O servico central e `src/services/audit_service.py`.
- O log sanitiza senha, token e segredos.
- CPF e CNPJ sao gravados mascarados ou protegidos.
- A pagina de auditoria permite filtros por usuario, tabela, acao, registro e data.

## Roadmap de endurecimento

1. Expandir cobertura de testes de API.
2. Adicionar fluxo controlado de visualizacao sem mascara com auditoria dedicada.
3. Evoluir recuperacao de senha e troca forçada no primeiro acesso.
4. Adicionar migracoes incrementais reais para novas evolucoes do schema.
