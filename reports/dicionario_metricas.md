# Dicionário de Métricas

## Efetivo Inicial
- Descrição: Headcount no início do período.
- Fórmula: Valor extraído das abas resumo ou rotatividade.
- Fonte: Resumo/rotatividade.
- Limitações: Pode divergir quando há erro de fórmula.
- Extraída ou calculada: extraída

## Efetivo Final
- Descrição: Headcount no fim do período.
- Fórmula: Valor extraído das abas resumo.
- Fonte: Resumo de indicadores.
- Limitações: Depende da consistência de admissões e desligamentos.
- Extraída ou calculada: extraída

## Efetivo Médio
- Descrição: Média entre efetivo inicial e final.
- Fórmula: (Efetivo Inicial + Efetivo Final) / 2
- Fonte: Resumo ou calculado pelo pipeline.
- Limitações: Quando recalculado, usa apenas headcount disponível.
- Extraída ou calculada: extraída/calculada

## Admissões
- Descrição: Entradas no mês.
- Fórmula: Novas Contratações (Un) ou Admissões.
- Fonte: Resumo/rotatividade.
- Limitações: Pode não refletir subáreas sem aba própria.
- Extraída ou calculada: extraída

## Desligamentos
- Descrição: Saídas no mês.
- Fórmula: Desligamentos (Un) ou Desligamentos.
- Fonte: Resumo/rotatividade.
- Limitações: Erros em rotatividade afetam a taxa.
- Extraída ou calculada: extraída

## Turnover
- Descrição: Rotatividade principal.
- Fórmula: ((Desligamentos + Admissões) / 2) / Total de Colaboradores
- Fonte: Resumo/rotatividade.
- Limitações: Se Total de Colaboradores estiver ausente, manter inconsistente.
- Extraída ou calculada: extraída/calculada

## Turnover Ajustado
- Descrição: Rotatividade com efetivo médio.
- Fórmula: ((Desligamentos + Admissões) / 2) / Efetivo Médio
- Fonte: calculado_pelo_pipeline.
- Limitações: Só existe quando há efetivo médio.
- Extraída ou calculada: calculada

## Afastamentos
- Descrição: Ausências por afastamento.
- Fórmula: Valor da planilha.
- Fonte: Resumo/afastamentos.
- Limitações: Em algumas abas vem somado com faltas.
- Extraída ou calculada: extraída

## Faltas
- Descrição: Faltas no período.
- Fórmula: Valor da planilha.
- Fonte: Resumo.
- Limitações: Nem sempre separado dos afastamentos.
- Extraída ou calculada: extraída

## Férias
- Descrição: Dias não produtivos por férias.
- Fórmula: Valor da planilha.
- Fonte: Resumo.
- Limitações: Pode estar zerado em meses sem férias lançadas.
- Extraída ou calculada: extraída

## Dias Programados
- Descrição: Dias previstos para trabalho.
- Fórmula: Valor da planilha.
- Fonte: Resumo.
- Limitações: Pode ser calculado via efetivo médio em algumas abas.
- Extraída ou calculada: extraída

## Dias Produtivos
- Descrição: Dias efetivamente produtivos.
- Fórmula: Dias Programados - Dias não Produtivos
- Fonte: Resumo/calculado.
- Limitações: Mantido como extraído quando confiável.
- Extraída ou calculada: extraída/calculada

## Dias não Produtivos
- Descrição: Dias perdidos.
- Fórmula: Afastamentos + Faltas + Férias quando explícito.
- Fonte: Resumo.
- Limitações: Não supõe faltas se a planilha não separar.
- Extraída ou calculada: extraída

## Horas Programadas
- Descrição: Horas previstas.
- Fórmula: Valor da planilha.
- Fonte: Resumo/rotatividade.
- Limitações: Não arredondado internamente.
- Extraída ou calculada: extraída

## Horas não Produtivas
- Descrição: Horas perdidas.
- Fórmula: Valor da planilha ou cálculo proporcional explícito.
- Fonte: Resumo/rotatividade.
- Limitações: Sem regra explícita, não converte dias em horas.
- Extraída ou calculada: extraída

## Taxa de Absenteísmo
- Descrição: Percentual de horas ou dias perdidos.
- Fórmula: Horas não Produtivas / Horas Programadas; fallback Dias não Produtivos / Dias Programados
- Fonte: Resumo/rotatividade/calculado.
- Limitações: Só usa fallback se não houver horas.
- Extraída ou calculada: extraída/calculada

## Folha Líquida
- Descrição: Valor líquido da folha.
- Fórmula: Valor da planilha.
- Fonte: Resumo/Fopag Analitic.
- Limitações: Pode haver dependência de fórmulas legadas.
- Extraída ou calculada: extraída

## Folha Bruta
- Descrição: Valor bruto da folha.
- Fórmula: Valor da planilha.
- Fonte: Resumo/Fopag.
- Limitações: Pode depender de consolidações legadas.
- Extraída ou calculada: extraída

## Salário Per Capita
- Descrição: Folha por efetivo.
- Fórmula: Folha Bruta / Efetivo considerado
- Fonte: Resumo/calculado.
- Limitações: Sem efetivo confiável, manter inconsistente.
- Extraída ou calculada: extraída/calculada

## Comissão
- Descrição: Comissões comerciais.
- Fórmula: Valor da planilha.
- Fonte: Resumo Comercial/Custo.
- Limitações: Pode estar ausente em meses sem apuração.
- Extraída ou calculada: extraída

## DSR
- Descrição: Descanso semanal remunerado associado.
- Fórmula: Valor da planilha.
- Fonte: Resumo Comercial.
- Limitações: Pode estar zerado.
- Extraída ou calculada: extraída

## Hora Extra
- Descrição: Horas extras.
- Fórmula: Valor da planilha.
- Fonte: Resumo Comercial/Fabril.
- Limitações: Timedelta convertido para horas.
- Extraída ou calculada: extraída

## Hora Extra + DSR
- Descrição: Custo financeiro de HE + DSR.
- Fórmula: Valor da planilha.
- Fonte: Resumo Comercial/Fabril.
- Limitações: Pode estar zerado em meses sem evento.
- Extraída ou calculada: extraída

## Valor de Tributos
- Descrição: Soma dos tributos da folha.
- Fórmula: Valor da planilha.
- Fonte: Resumo.
- Limitações: Erros #REF! precisam correção manual.
- Extraída ou calculada: extraída

## INSS Patronal
- Descrição: Encargo patronal de INSS.
- Fórmula: Valor da planilha.
- Fonte: Resumo/Fopag/Custo.
- Limitações: Pode não existir separado em todas as áreas.
- Extraída ou calculada: extraída

## FGTS
- Descrição: Encargo FGTS.
- Fórmula: Valor da planilha.
- Fonte: Resumo/Fopag/Custo.
- Limitações: Erros de fórmula afetam a visão mensal.
- Extraída ou calculada: extraída

## Encargos sobre Folha %
- Descrição: Percentual de encargos.
- Fórmula: Valor de Tributos / Folha Bruta
- Fonte: Resumo/calculado.
- Limitações: Mantido inconsistente em divisão por zero.
- Extraída ou calculada: extraída/calculada

## Custo Total
- Descrição: Soma do custo da folha e correlatos.
- Fórmula: Linha total ou soma das categorias quando confiável.
- Fonte: Custo Fopag/Custo.
- Limitações: Quando total não é confiável, usa soma das categorias.
- Extraída ou calculada: extraída/calculada

## Custo / Faturamento %
- Descrição: Participação do custo no faturamento.
- Fórmula: Custo Total / Faturamento
- Fonte: Custo Fopag.
- Limitações: Sem faturamento, manter pendente.
- Extraída ou calculada: extraída/calculada

## Faturamento por Colaborador
- Descrição: Produtividade financeira por pessoa.
- Fórmula: Faturamento / Colaboradores
- Fonte: Custo Fopag.
- Limitações: Sem colaboradores ou faturamento, manter pendente.
- Extraída ou calculada: extraída/calculada

## Benefícios
- Descrição: Custo agregado de benefícios.
- Fórmula: Soma das colunas de benefício.
- Fonte: TB_Elegibilidade/Fopag.
- Limitações: Pode variar conforme layout da aba.
- Extraída ou calculada: extraída/calculada

## Provisões
- Descrição: Provisões de férias/13º e similares.
- Fórmula: Valor da planilha.
- Fonte: Custo Fopag/Fopag.
- Limitações: Agrupa apenas o que estiver explícito.
- Extraída ou calculada: extraída

## Premiação
- Descrição: Premiações e incentivos.
- Fórmula: Valor da planilha.
- Fonte: Custo Fopag/Premiação CLT/MEI.
- Limitações: MEI só entra quando há valores na aba.
- Extraída ou calculada: extraída

## Terceiros
- Descrição: Custos com terceiros.
- Fórmula: Categorias MEI/Freelancer/Terceiros.
- Fonte: Custo Fopag/Terceiros.
- Limitações: Nem todas as abas trazem período explícito.
- Extraída ou calculada: extraída
