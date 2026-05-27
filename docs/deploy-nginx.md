# Deploy Nginx

## Objetivo

Exemplo opcional de reverse proxy para API, app operacional e dashboard legado.

## Arquivo

- `deploy/nginx/dash_rh.conf.example`

## Regras

- nao inclui dominio real
- nao inclui certificado real
- nao inclui senha
- HTTPS deve ser configurado externamente conforme a infraestrutura interna

## Rotas sugeridas

- `/api/` -> API FastAPI
- `/operacional/` -> app operacional Streamlit
- `/dashboard/` -> dashboard legado Streamlit

## Observacoes

- ajuste `server_name`, upstreams e politica de HTTPS conforme o ambiente
- mantenha a API atras de rede interna ou proxy autenticado quando possivel
