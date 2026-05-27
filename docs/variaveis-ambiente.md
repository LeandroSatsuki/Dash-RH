# Variaveis de Ambiente

## Minimas

- `APP_ENV`
- `DATABASE_URL`
- `SECRET_KEY`
- `UPLOAD_DIR`
- `BACKUP_DIR`
- `ADMIN_NAME`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `LOG_LEVEL`

## Notificacoes externas

- `SMTP_ENABLED`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_FROM`
- `WEBHOOK_ENABLED`
- `WEBHOOK_URL`

## Docker Compose

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

## Regras

- nao versionar `.env`
- nao usar `Admin@123` em producao
- nao usar `change-me` em `SECRET_KEY` de producao
- notificacoes externas ficam desativadas por padrao
