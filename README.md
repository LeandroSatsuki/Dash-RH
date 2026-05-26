# Dash-RH Operacional

Sistema hibrido de RH/DP com duas frentes:

1. Dashboard legado e pipeline analitico por planilhas.
2. Mini ERP operacional com banco de dados, autenticacao, CRUD, auditoria e fluxos reais de DP/RH.

## Instalacao

```bash
python -m pip install -r requirements.txt
```

## Ambiente

Crie um `.env` a partir de `.env.example`.

SQLite local:

```env
DATABASE_URL=sqlite:///./data/app/dash_rh.db
APP_ENV=development
SECRET_KEY=change-me
UPLOAD_DIR=data/uploads
ADMIN_NAME=Administrador
ADMIN_EMAIL=admin@local.test
ADMIN_PASSWORD=Admin@123
```

PostgreSQL:

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

```bash
python -m src.db.init_db
```

Regras:

- Em `development`, fallback do admin inicial e permitido.
- Fora de `development`, `ADMIN_EMAIL` e `ADMIN_PASSWORD` sao obrigatorios.
- Em `production`, `Admin@123` e bloqueada.

## Migracoes

```bash
alembic revision --autogenerate -m "descricao"
alembic upgrade head
```

## Seed demo

Para demonstracao local com dados totalmente ficticios:

```bash
python scripts/seed_demo.py
```

O seed:

- cria empresa fake, estrutura organizacional, colaboradores ficticios, beneficios, ferias, afastamentos, desligamentos, folha e auditoria
- grava documentos demo sem conteudo sensivel real
- e bloqueado em `APP_ENV=production`

## Fluxo operacional

Fluxos principais desta fase:

- admissao com pre-cadastro, checklist, conclusao e historico funcional
- ferias com solicitacao, aprovacao, cancelamento e conclusao
- afastamentos com retorno, documento e impacto operacional
- beneficios com vinculo, custo e encerramento
- folha por competencia com snapshot, bloqueio de fechamento e exportacao
- desligamento com conclusao, encerramento de beneficios e historico
- indicadores operacionais vindos do banco

## Execucao

Pipeline legado:

```bash
python main.py
```

Dashboard legado:

```bash
streamlit run dashboard/app.py
```

App operacional:

```bash
streamlit run operational_app/app.py
```

API:

```bash
uvicorn src.api.main:app --reload
```

## Testes e check local

```bash
pytest
python scripts/check_local.py
```

## Seguranca e LGPD

- Login obrigatorio permanece ativo no app operacional.
- CPF, CNPJ, e-mail, telefone, salario e dados medicos permanecem mascarados por padrao na interface.
- Uploads usam validacao de extensao, tamanho e path seguro.
- Operacoes criticas registram auditoria.
- Planilhas, `.env`, bancos locais e uploads permanecem fora do Git.
