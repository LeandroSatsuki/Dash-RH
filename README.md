# Projeto RH / Folha de Pagamento

Projeto Python para ingestão auditável de planilhas Excel de RH/Folha, geração de fatos normalizados, relatório de qualidade e dashboard executivo em Streamlit.

## Requisitos

- Python 3.11+
- Dependências em `requirements.txt`

## Instalação

```bash
python -m pip install -r requirements.txt
```

## Onde colocar os arquivos

- Coloque os `.xlsx` na raiz do projeto ou diretamente em `data/raw/`.
- Ao rodar `python main.py`, o pipeline copia automaticamente os workbooks da raiz para `data/raw/` sem mover os originais.

## Execução do pipeline

```bash
python main.py
```

## Abrir o dashboard

```bash
streamlit run dashboard/app.py
```

## Arquivos gerados

- `data/processed/catalogo_abas.csv`
- `data/processed/erros_celulas.csv`
- `data/processed/*.csv`
- `data/processed/*.parquet`
- `reports/qualidade_dados.md`
- `reports/qualidade_dados.json`
- `reports/dicionario_metricas.md`
- `reports/resumo_executivo.html`
- `reports/resumo_executivo.xlsx`

## Como interpretar os alertas

- `Dado pendente / inconsistente`: o valor veio de célula com erro, referência quebrada, divisão por zero ou fonte insuficiente.
- `calculado_pelo_pipeline`: o valor foi recalculado com regra explícita e rastreável.
- `inferido_com_contexto`: o valor usa contexto forte do workbook, mas sem marcação explícita na aba.

## Limitações conhecidas

- Algumas abas mensais têm nomenclatura heterogênea e nem sempre trazem ano explícito.
- Fórmulas antigas com `#REF!` e `#DIV/0!` não são corrigidas automaticamente.
- Nem todas as abas separam afastamentos e faltas em colunas distintas.
- Premiação MEI só é promovida a indicador quando a aba contém valores numéricos explícitos.

