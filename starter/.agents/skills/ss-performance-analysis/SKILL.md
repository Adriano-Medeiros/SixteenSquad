---
name: "ss-performance-analysis"
description: "Investigar lentidão, consumo de recursos ou avaliar uma otimização com medições."
---

# AG-14 — Performance Specialist

## Entradas

Sintoma, meta, cenário/carga, ambiente e medições disponíveis. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Definir métrica e cenário comparável: latência/percentis, throughput, memória ou frame time, conforme o problema.
2. Separar hipótese de medição; identificar aquecimento, tamanho da amostra e fatores de confusão do ambiente.
3. Usar ferramentas existentes para localizar o custo dominante quando medir estiver autorizado; caso contrário, propor experimento.
4. Aplicar uma mudança de cada vez no escopo permitido e preservar comportamento, inclusive casos de borda.
5. Comparar antes/depois sob mesmas condições, apresentar variação e regressões. Ausência de medição permanece estimativa.

## Saída e conclusão

Hipótese priorizada, experimento delimitado e comparação com limites explícitos.

Concluir quando: Conclusões têm cenário, medida e incerteza; melhoria não sacrifica correção sem decisão explícita.

## Limites e referências

Não gerar carga em produção, prometer ganhos ou trocar arquitetura antes de evidência.

Consultar métricas fornecidas, requisitos de performance e ferramentas do projeto. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
