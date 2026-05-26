# Dash-RH Operacional

Sistema hibrido de RH/DP com duas frentes:

1. Dashboard legado e pipeline analitico por planilhas.
2. Mini ERP operacional com banco de dados, autenticacao, CRUD, auditoria e importacao legada.

## Objetivo

Reduzir a dependencia de planilhas para registros operacionais de RH/DP, mantendo compatibilidade com o legado e sem remover o dashboard atual.

## Instalacao

```bash
python -m pip install -r requirements.txt
```

## Ambiente

Crie um `.env` a partir de `.env.example`.

Exemplo para SQLite local:

```env
DATABASE_URL=sqlite:///./data/app/dash_rh.db
APP_ENV=development
SECRET_KEY=change-me
UPLOAD_DIR=data/uploads
ADMIN_NAME=Administrador
ADMIN_EMAIL=admin@local.test
ADMIN_PASSWORD=Admin@123
```

Exemplo para PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://dashrh_user:change-me@localhost:5432/dash_rh
APP_ENV=production
SECRET_KEY=troque-esta-chave
UPLOAD_DIR=data/uploads
ADMIN_NAME=Administrador
ADMIN_EMAIL=admin@empresa.local
ADMIN_PASSWORD=uma-senha-forte
```

## Banco e admin

Inicializacao simples para desenvolvimento:

```bash
python -m src.db.init_db
```

Regras de seguranca do admin inicial:

- Em `APP_ENV=development`, o sistema aceita fallback de `ADMIN_EMAIL` e `ADMIN_PASSWORD`.
- Em qualquer ambiente fora de `development`, `ADMIN_PASSWORD` e obrigatoria.
- Em `APP_ENV=production`, a senha `Admin@123` e bloqueada.
- A senha nunca e impressa em logs.

## Migracoes Alembic

Gerar uma nova revisao:

```bash
alembic revision --autogenerate -m "initial schema"
```

Aplicar migracoes:

```bash
alembic upgrade head
```

Use `init_db` para bootstrap local rapido e `alembic` para ambientes compartilhados e controle versionado.

## Pipeline legado

```bash
python main.py
```

## Dashboard legado

```bash
streamlit run dashboard/app.py
```

## App operacional

```bash
streamlit run operational_app/app.py
```

O app operacional exige login antes de exibir paginas ou dados.

## API FastAPI

```bash
uvicorn src.api.main:app --reload
```

Healthcheck:

```bash
curl http://127.0.0.1:8000/health
```

## Fluxo de importacao

1. Acesse o app operacional.
2. Abra `Configuracoes`.
3. Faca upload da planilha legada.
4. Revise validacoes e erros.
5. Execute a importacao.
6. Consulte a auditoria e o relatorio final.

## Testes e check local

```bash
pytest
python scripts/check_local.py
```

## Seguranca e LGPD

- Planilhas, uploads, bancos locais e `.env` permanecem fora do Git.
- CPF, CNPJ, e-mail, telefone, salario e dados medicos permanecem mascarados por padrao.
- Senhas usam hash seguro.
- Alteracoes criticas e eventos de autenticacao sao auditados.
- Uploads ficam restritos a `UPLOAD_DIR`, com extensoes permitidas e hash SHA256.
- O modulo de eSocial gera apenas preparacao e validacao interna, sem envio oficial automatico.
