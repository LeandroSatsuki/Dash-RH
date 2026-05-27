# Auditoria Fase 6 - Deploy, Producao, Backup e Observabilidade

## Estrutura atual do projeto

- `main.py`: pipeline legado de leitura e transformacao de planilhas.
- `dashboard/app.py`: dashboard legado em Streamlit.
- `operational_app/app.py`: app operacional em Streamlit com login obrigatorio.
- `src/api/main.py`: API FastAPI.
- `src/db`, `migrations`: banco SQLAlchemy e Alembic.
- `src/crud`, `src/services`, `src/schemas`, `src/auth`: backend operacional.
- `scripts/`: automacoes locais como seed, checks e rotinas operacionais.
- `tests/`: suite automatizada do projeto.

## Apps que precisam subir

- API FastAPI.
- App operacional Streamlit.
- Dashboard legado Streamlit.
- PostgreSQL em producao ou homologacao.

## Portas usadas

- API: `8000` por convencao e validacoes anteriores.
- App operacional: `8501` por convencao.
- Dashboard legado: `8502` por convencao.
- PostgreSQL: `5432` em ambiente controlado.

## Variaveis de ambiente atuais

- `DATABASE_URL`
- `APP_ENV`
- `SECRET_KEY`
- `UPLOAD_DIR`
- `ADMIN_NAME`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `SMTP_ENABLED`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_FROM`
- `WEBHOOK_ENABLED`
- `WEBHOOK_URL`

## Dependencias atuais

- `fastapi`, `uvicorn`
- `streamlit`
- `sqlalchemy`, `alembic`
- `psycopg[binary]`
- `pandas`, `numpy`, `openpyxl`, `pyarrow`
- `pytest`

## Arquivos e diretorios sensiveis

- `.env`
- `data/raw/`
- `data/processed/`
- `data/uploads/`
- `data/app/`
- `reports/*.xlsx`
- `reports/*.csv`
- `reports/*.json`
- logs locais em `*.log`

## Diretorios que precisam persistir

- `data/uploads/`
- `data/app/` quando SQLite for usado em desenvolvimento
- `data/logs/` quando logging em arquivo for habilitado
- `data/backups/` para rotina de backup

## Riscos de producao

- `src/api/main.py` executa `init_db()` na importacao, o que mistura bootstrap com startup HTTP.
- `src/utils/config.py` ainda e simplificado e nao valida cenarios de producao.
- `src/db/database.py` cria engine global sem camada central de configuracao validada.
- Ainda nao ha contêineres versionados para API, app operacional, dashboard e PostgreSQL.
- Nao ha rotina padronizada versionada para migracao em deploy.

## Riscos de backup

- Nao existe script versionado de backup ou restore.
- Nao ha `BACKUP_DIR` centralizado.
- SQLite e PostgreSQL ainda nao tem politica distinta de backup documentada.

## Riscos de LGPD

- Nao ha sanitizacao central de logs para CPF, salario, segredos e URLs sensiveis.
- Healthcheck atual e simples e nao diferencia readiness de liveness.
- Startups e scripts ainda usam `print`, o que dificulta controle fino de exposicao.

## Riscos de logs com dados sensiveis

- Nao existe `logging_config.py` central.
- Scripts e bootstrap usam mensagens diretas em console.
- Nao ha garantia uniforme de mascaramento em payloads de erro e observabilidade.

## Estado atual das migracoes Alembic

- `migrations/env.py` ja usa `Base.metadata` e le `DATABASE_URL`.
- Existe migration inicial real no repositorio.
- Ainda falta script operacional de migracao para deploy.

## Estado atual do `.gitignore`

- Ja protege `.env`, bancos locais, uploads, logs, planilhas, artefatos de reports e caches.
- Ainda precisa cobrir explicitamente diretorios futuros de backup e logs persistidos.

## Estado atual dos testes

- Suite atual: `126 passed`.
- `scripts/check_local.py` ja valida imports, permissoes, seed bloqueado em producao e `pytest`.
- Ainda nao valida deploy, backup, restore, health readiness, seguranca de producao ou padroes sensiveis no Git.

## Recomendacoes para a fase

1. Centralizar configuracao e validacao em `src/utils/config.py`.
2. Criar logging sanitizado e reaproveitavel para API e scripts.
3. Separar healthcheck de liveness e readiness.
4. Criar scripts dedicados para migration, backup, restore e security check.
5. Versionar Dockerfiles e `docker-compose` com volumes e healthchecks.
6. Documentar deploy interno, backup, restore e runbook operacional.
