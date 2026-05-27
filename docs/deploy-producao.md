# Deploy Producao

## Requisitos

- Docker e Docker Compose
- PostgreSQL recomendado para producao
- `.env` configurado fora do Git

## Passos

1. Criar `.env` a partir de `.env.example`.
2. Ajustar `DATABASE_URL`, `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `UPLOAD_DIR` e `BACKUP_DIR`.
3. Rodar `python scripts/security_check.py`.
4. Subir a stack com `docker compose build` e `docker compose up -d`.
5. Aplicar migracoes com `python scripts/migrate.py` ou pelo container da API.
6. Validar `GET /health` e `GET /health/ready`.
7. Acessar:
   - API em `:8000`
   - app operacional em `:8501`
   - dashboard legado em `:8502`

## Observacoes

- notificacoes externas seguem desativadas por padrao
- SQLite deve ficar restrito ao desenvolvimento local
- o modulo de ponto continua apenas operacional interno
