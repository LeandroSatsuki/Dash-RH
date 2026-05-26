# Auditoria Técnica da Fase 2 de Estabilização

## Estrutura atual do projeto

```text
Dash-RH/
  dashboard/
    app.py
  operational_app/
    app.py
    auth.py
    common.py
    pages/
  src/
    api/
    auth/
    crud/
    db/
    extract/
    schemas/
    services/
    transform/
    utils/
    validate/
  migrations/
  docs/
  tests/
  main.py
  README.md
  requirements.txt
  alembic.ini
```

## Rotas API existentes

- `/health`
- `/auth/login`
- `/auth/me`
- `/departamentos`
- `/cargos`
- `/centros-custo`
- `/colaboradores`
- `/beneficios`
- `/beneficios/vinculos`
- `/ferias`
- `/afastamentos`
- `/folha/competencias`
- `/folha/competencias/{id}/fechar`
- `/folha/competencias/{id}/reabrir`
- `/folha/rubricas`
- `/folha/lancamentos`
- `/documentos`
- `/indicadores`

## Páginas Streamlit existentes

App operacional:

- Home
- Cadastros
- Colaboradores
- Admissões
- Férias
- Afastamentos
- Benefícios
- Folha
- Desligamentos
- Documentos
- Indicadores
- Qualidade de dados
- Configurações
- Qualidade Operacional
- Auditoria

Dashboard legado:

- `dashboard/app.py`

## Modelos SQLAlchemy existentes

- `usuarios`
- `empresas`
- `departamentos`
- `cargos`
- `centros_custo`
- `colaboradores`
- `historico_funcional`
- `admissoes`
- `ferias`
- `afastamentos`
- `beneficios`
- `colaborador_beneficios`
- `competencias_folha`
- `rubricas`
- `lancamentos_folha`
- `desligamentos`
- `documentos`
- `auditoria`
- `importacoes`
- `folha_snapshots`

## CRUDs existentes

- `departamentos`
- `cargos`
- `centros_custo`
- `colaboradores`
- `beneficios`
- `ferias`
- `afastamentos`
- `folha`
- `desligamentos`
- `documentos`
- `auditoria`

## Services existentes

- `masking`
- `auditoria`
- `audit_service`
- `validacoes_dp`
- `indicadores`
- `importacao_excel`
- `esocial_mapping`
- `file_storage`
- `data_quality`

## Testes existentes

- `test_utils.py`
- `test_colaboradores.py`
- `test_ferias.py`
- `test_afastamentos.py`
- `test_folha.py`
- `test_indicadores.py`
- `test_masking.py`
- `test_importacao_excel.py`

## Verificações realizadas

- Imports principais compilam.
- App operacional abre sem depender de `data/processed`.
- Dashboard legado continua independente e funcional.
- `src/db/init_db.py` funciona com banco limpo.
- Testes usam banco isolado em memória.
- Não foram identificados caminhos absolutos no código operacional novo.
- Havia credenciais padrão perigosas no login Streamlit e no bootstrap do admin.
- Há exemplos de admin de desenvolvimento em docs, mas sem exposição de dados reais.
- Não foram encontrados dados pessoais reais hardcoded em testes ou documentação nova.

## Pontos de risco identificados

- Admin inicial inseguro fora de desenvolvimento.
- Login Streamlit com senha padrão preenchida.
- Auditoria inicial espalhada e sem sanitização central.
- Permissões por perfil ainda simplificadas.
- Upload de documentos sem storage central seguro.
- Alembic existia sem migração real inicial.
- Campos monetários misturavam `float` lógico com `Numeric` no banco.

## Pontos quebráveis

- Fechamento de competência sem snapshot financeiro.
- Operações críticas dependendo só de proteção de tela, sem padronização total de autorização.
- Evolução de produção com PostgreSQL sem documentação suficiente.
- Qualidade operacional ainda pouco visível para saneamento diário.

## Dívida técnica

- Alguns módulos ainda estão em nível MVP.
- Parte das rotas API ainda usa gating por perfil em vez de permissão granular por recurso.
- O app operacional ainda pode receber mais filtros, tratamento de erros e UX de edição.
- Falta aprofundar auditoria de visualização sem máscara em todos os pontos sensíveis.

## Recomendações de correção

1. Bloquear fallback inseguro do admin fora de desenvolvimento.
2. Centralizar auditoria com sanitização.
3. Fortalecer permissões por matriz de acesso.
4. Padronizar dinheiro com `Decimal`.
5. Proteger upload com service dedicado e validação de extensão/tamanho.
6. Criar migração inicial real do Alembic.
7. Expor qualidade operacional como módulo visível.
8. Adicionar script local de verificação contínua.
