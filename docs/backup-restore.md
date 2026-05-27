# Backup e Restore

## Backup

Comando:

```bash
python scripts/backup_postgres.py
```

- PostgreSQL usa `pg_dump`
- SQLite local usa copia do arquivo para desenvolvimento
- backups vao para `BACKUP_DIR`
- nao salve backup em pasta versionada

## Restore

Comando:

```bash
python scripts/restore_postgres.py --file caminho --confirm
```

- exige confirmacao explicita
- nao imprime credenciais
- em PostgreSQL usa `pg_restore`

## Riscos

- restore sobrescreve o estado atual do banco
- execute apenas em janela controlada
- valide permissao e destino antes do uso

## Periodicidade recomendada

- diaria para ambiente interno com uso operacional
- adicional antes de migracoes ou manutencoes maiores
