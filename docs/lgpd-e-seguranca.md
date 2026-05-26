# LGPD e Seguranca

## Dados sensiveis

O sistema trata como sensiveis, entre outros:

- CPF
- CNPJ
- salario
- dados medicos
- dados bancarios
- documentos pessoais

## Mascaramento

- CPF, CNPJ, e-mail, telefone e dados bancarios usam mascaramento por padrao.
- Salario e valores sensiveis nao devem ser exibidos em bruto para perfis sem permissao.
- Dados medicos devem permanecer mascarados ou resumidos na interface.

## Perfis e acesso

- O app operacional exige login.
- A API exige token.
- O acesso a modulos e acoes segue matriz por perfil.
- Perfis com acesso parcial usam visoes mascaradas ou limitadas.

## Auditoria

Sao auditados:

- criacao
- edicao
- soft delete
- login
- falha de login
- fechamento de competencia
- reabertura de competencia
- importacao de planilha
- upload de documento

## Documentos

- Arquivos ficam restritos a `UPLOAD_DIR`.
- O caminho e validado para bloquear path traversal.
- O nome interno e seguro e separado do nome original.
- O hash SHA256 do arquivo fica armazenado.
- Extensoes permitidas sao controladas.

## Backup e operacao

- Nao usar SQLite em producao compartilhada.
- Ativar backup do banco e da pasta de uploads.
- Restringir o acesso do app e da API a rede interna ou VPN.
- Revisar periodicamente perfis, logs e retencao documental.

## Recomendacoes de producao

- Trocar `SECRET_KEY`.
- Definir `ADMIN_PASSWORD` forte.
- Usar PostgreSQL.
- Ativar HTTPS e proxy reverso.
- Validar politicas de retencao e descarte.
- Manter planilhas, `.env`, bancos locais e uploads fora do Git.
