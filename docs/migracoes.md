# Migracoes

## Quando usar `init_db`

Use `python -m src.db.init_db` em desenvolvimento local quando voce precisa:

- criar rapidamente o banco SQLite local
- criar as tabelas do schema atual
- bootstrapar o usuario admin inicial

Esse fluxo e pratico para ambiente local, mas nao substitui controle versionado de schema.

## Quando usar Alembic

Use Alembic quando voce precisa:

- versionar alteracoes de schema
- aplicar mudancas em homologacao ou producao
- alinhar SQLite e PostgreSQL com revisoes conhecidas
- distribuir evolucoes do banco com rastreabilidade

## Comandos principais

Gerar revisao:

```bash
alembic revision --autogenerate -m "initial schema"
```

Aplicar migracoes:

```bash
alembic upgrade head
```

Ver historico:

```bash
alembic history
```

Ver revisao atual:

```bash
alembic current
```

## SQLite local x PostgreSQL

- SQLite e adequado para desenvolvimento local, testes manuais e MVP individual.
- PostgreSQL e a opcao recomendada para producao, uso multiusuario, backup consistente e maior robustez operacional.
- O projeto aceita ambos via `DATABASE_URL`.

## Fluxo recomendado

1. Desenvolva localmente.
2. Gere a revisao Alembic.
3. Revise o arquivo em `migrations/versions/`.
4. Rode `alembic upgrade head`.
5. Valide `python -m src.db.init_db` para bootstrap local quando necessario.
