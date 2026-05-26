# Dicionário de Dados

## usuarios
- `id`: chave primária
- `nome`: nome do usuário
- `email`: identificador único de login
- `senha_hash`: hash seguro da senha
- `perfil`: perfil de acesso
- `ativo`: indicador de ativação
- `criado_em`, `atualizado_em`: trilha temporal

## empresas
- `id`, `razao_social`, `nome_fantasia`, `cnpj`, `status`, `criado_em`, `atualizado_em`, `deletado_em`

## departamentos
- `id`, `nome`, `descricao`, `gestor_id`, `status`, `criado_em`, `atualizado_em`, `deletado_em`

## cargos
- `id`, `nome`, `cbo`, `departamento_id`, `descricao`, `status`, `criado_em`, `atualizado_em`, `deletado_em`

## centros_custo
- `id`, `codigo`, `nome`, `area`, `subarea`, `status`, `criado_em`, `atualizado_em`, `deletado_em`

## colaboradores
- `id`, `matricula`, `nome_completo`, `nome_social`, `cpf`, `rg`, `data_nascimento`, `email`, `telefone`, `endereco`, `cidade`, `uf`, `regime_contratual`, `tipo_vinculo`, `data_admissao`, `data_desligamento`, `cargo_id`, `departamento_id`, `centro_custo_id`, `salario_base`, `jornada_semanal`, `gestor_id`, `status`, `origem`, `criado_em`, `atualizado_em`, `deletado_em`

## historico_funcional
- `id`, `colaborador_id`, `tipo_evento`, `data_evento`, `data_inicio`, `data_fim`, `campo_alterado`, `valor_anterior`, `valor_novo`, `motivo`, `usuario_id`, `criado_em`

## admissoes
- `id`, `colaborador_id`, `data_prevista_admissao`, `data_admissao`, `status`, `checklist_json`, `observacao`, `criado_em`, `atualizado_em`

## ferias
- `id`, `colaborador_id`, `periodo_aquisitivo_inicio`, `periodo_aquisitivo_fim`, `data_limite_gozo`, `dias_direito`, `dias_gozados`, `dias_restantes`, `data_inicio`, `data_fim`, `abono_pecuniario`, `adiantamento_13`, `status`, `observacao`, `criado_em`, `atualizado_em`, `deletado_em`

## afastamentos
- `id`, `colaborador_id`, `tipo`, `data_inicio`, `data_fim`, `quantidade_dias`, `quantidade_horas`, `impacta_folha`, `impacta_absenteismo`, `cid_mascarado`, `status`, `observacao`, `criado_em`, `atualizado_em`, `deletado_em`

## beneficios
- `id`, `nome`, `tipo`, `operadora`, `status`, `criado_em`, `atualizado_em`

## colaborador_beneficios
- `id`, `colaborador_id`, `beneficio_id`, `data_inicio`, `data_fim`, `valor_empresa`, `valor_colaborador`, `dependentes`, `status`, `observacao`, `criado_em`, `atualizado_em`

## competencias_folha
- `id`, `ano`, `mes`, `competencia`, `status`, `data_abertura`, `data_fechamento`, `usuario_fechamento_id`, `observacao`, `criado_em`, `atualizado_em`

## rubricas
- `id`, `codigo`, `descricao`, `tipo`, `natureza`, `incide_inss`, `incide_fgts`, `incide_irrf`, `ativo`, `criado_em`, `atualizado_em`

## lancamentos_folha
- `id`, `competencia_id`, `colaborador_id`, `rubrica_id`, `tipo`, `valor`, `quantidade`, `origem`, `observacao`, `criado_em`, `atualizado_em`, `deletado_em`

## desligamentos
- `id`, `colaborador_id`, `data_aviso_previo`, `data_desligamento`, `tipo_rescisao`, `motivo`, `exame_demissional`, `entrevista_realizada`, `status`, `valor_estimado_rescisao`, `observacao`, `criado_em`, `atualizado_em`

## documentos
- `id`, `colaborador_id`, `tipo_documento`, `nome_original`, `nome_armazenado`, `caminho_arquivo`, `hash_arquivo`, `validade`, `status`, `usuario_upload_id`, `criado_em`, `atualizado_em`, `deletado_em`

## auditoria
- `id`, `usuario_id`, `tabela`, `registro_id`, `acao`, `campo_alterado`, `valor_anterior`, `valor_novo`, `ip`, `origem`, `criado_em`

## importacoes
- `id`, `nome_arquivo`, `tipo_importacao`, `status`, `total_linhas`, `linhas_importadas`, `linhas_com_erro`, `relatorio_erros`, `usuario_id`, `criado_em`
