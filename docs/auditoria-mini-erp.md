# Auditoria Inicial do Projeto Dash-RH

## Objetivo desta auditoria

Mapear a situação atual do repositório antes da evolução para um mini ERP operacional de RH/DP, preservando o dashboard legado e o pipeline de importação por planilhas.

## Estrutura atual identificada

```text
Dash-RH/
  dashboard/
    app.py
  data/
    raw/
    processed/
  reports/
  src/
    dashboard/
    extract/
    transform/
    utils/
    validate/
  tests/
  main.py
  README.md
  requirements.txt
```

## Arquivo principal do dashboard

- Dashboard legado: `dashboard/app.py`
- Pipeline principal: `main.py`

## Pipeline de dados atual

O pipeline atual é baseado em leitura de planilhas Excel colocadas na raiz do projeto ou em `data/raw/`.

Fluxo identificado:

1. `main.py` garante diretórios de trabalho.
2. `main.py` copia planilhas da raiz para `data/raw/`.
3. `src/extract/catalog.py` e `src/extract/read_excel.py` inspecionam workbooks e extraem dados.
4. `src/transform/normalize_indicators.py`, `normalize_costs.py`, `normalize_payroll.py`, `normalize_people.py` e `normalize_periods.py` transformam os dados.
5. `src/validate/quality.py` gera relatórios de qualidade.
6. `main.py` salva datasets processados e relatórios.
7. `dashboard/app.py` consome os arquivos processados para exibição em Streamlit.

## Onde os CSV/Parquet processados são gerados

Os arquivos processados são gerados por `main.py`, principalmente pela função `save_dataset`.

Destino identificado:

- `data/processed/*.csv`
- `data/processed/*.parquet`

Relatórios gerados em:

- `reports/qualidade_dados.md`
- `reports/qualidade_dados.json`
- `reports/dicionario_metricas.md`
- `reports/resumo_executivo.html`
- `reports/resumo_executivo.xlsx`

## Dependências atuais

Dependências listadas em `requirements.txt`:

- `pandas>=2.2`
- `openpyxl>=3.1`
- `numpy>=1.26`
- `plotly>=5.24`
- `streamlit>=1.44`
- `pyarrow>=16.0`
- `python-dateutil>=2.9`
- `xlsxwriter>=3.2`
- `pytest>=8.3`

## Banco de dados

Não foi identificado banco de dados no estado atual do projeto.

Evidências:

- Não há `sqlalchemy`, `alembic`, `create_engine`, `SessionLocal`, `DATABASE_URL` ou estrutura `src/db/`.
- Não há arquivos de configuração de migração.
- Não há arquivos `.db` versionados como parte da solução atual.

## Autenticação

Não foi identificada autenticação no estado atual do projeto.

Evidências:

- Não há módulo de usuários, login, perfis, permissões, token ou hash de senha.
- O dashboard legado abre diretamente sem controle de acesso.

## Camada de CRUD

Não foi identificada uma camada de CRUD operacional.

Evidências:

- O projeto atual é orientado a ETL local + visualização analítica.
- Não há módulos de persistência transacional para cadastro, edição, exclusão lógica ou auditoria operacional.

## Conclusão da auditoria

O projeto atual está estruturado como um pipeline analítico com dashboard executivo, não como sistema operacional transacional.

Pontos fortes para reaproveitamento:

- Pipeline de importação de Excel já funcional.
- Organização razoável por extração, transformação, validação e visualização.
- Geração de indicadores e relatórios já existente.

Lacunas para a evolução a mini ERP:

- Banco de dados inexistente.
- Ausência de autenticação e perfis.
- Ausência de modelos operacionais.
- Ausência de CRUD.
- Ausência de auditoria transacional.
- Ausência de camada de API.
- Ausência de app operacional separado do dashboard legado.

## Diretriz arquitetural recomendada

Manter duas frentes integradas:

1. Frente legada/analítica:
   - preservar `main.py`
   - preservar `dashboard/app.py`
   - manter ingestão de planilhas como legado/importação

2. Frente operacional:
   - introduzir banco relacional
   - introduzir modelos de RH/DP
   - introduzir CRUD, autenticação, auditoria e mascaramento
   - usar o banco como fonte principal para novos registros
   - usar planilhas somente como importação/migração/retroalimentação controlada
