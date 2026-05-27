# Runbook Operacional

## Reiniciar servicos

- Docker: `docker compose restart`
- Local:
  - `uvicorn src.api.main:app --reload`
  - `streamlit run operational_app/app.py`
  - `streamlit run dashboard/app.py`

## Ver logs

- Docker: `docker compose logs -f`
- Local: logs em console ou `data/logs` se `LOG_TO_FILE=true`

## Rodar migracoes

```bash
python scripts/migrate.py
```

## Rodar daily checks

```bash
python scripts/run_daily_checks.py
```

## Gerar backup

```bash
python scripts/backup_postgres.py
```

## Restaurar backup

```bash
python scripts/restore_postgres.py --file caminho --confirm
```

## Validar sistema no ar

- `GET /health`
- `GET /health/ready`
- app operacional abre com login
- dashboard legado abre

## Trocar senha admin

- atualizar `ADMIN_PASSWORD` no ambiente
- em producao, usar senha forte

## Desativar notificacoes externas

- `SMTP_ENABLED=false`
- `WEBHOOK_ENABLED=false`

## Se o banco cair

1. validar container ou servico do PostgreSQL
2. verificar ultimo backup
3. checar `security_check` e `health/ready`
4. restaurar apenas com janela controlada
