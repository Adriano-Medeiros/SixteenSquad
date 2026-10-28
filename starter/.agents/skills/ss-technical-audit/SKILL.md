---
name: "ss-technical-audit"
description: "Revisar um alvo técnico contra requisitos e evidências, com achados priorizados."
---

# AG-11 — Technical Auditor

## Entradas

Alvo exato, escopo, critérios, referências e evidências disponíveis. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Identificar arquivo/revisão ou conjunto examinado e critérios aplicáveis. Declarar participação anterior e limites de independência.
2. Comparar comportamento ou texto com requisitos, chamadores e evidências; procurar contradições e casos de falha plausíveis.
3. Registrar cada achado com esperado, observado, localização, impacto e reprodução ou evidência disponível. Não criar achado sem fundamento só para preencher lista.
4. Priorizar impeditivos e propor correção mínima, sem alterar o alvo durante a revisão. Separar melhorias opcionais de falhas.
5. Concluir sem achados no escopo, com impeditivos ou inconclusivo conforme cobertura. Correções posteriores pedem nova verificação afetada; o relatório não concede aprovação humana.

## Saída e conclusão

Relatório conciso com achados, localizações, gravidade, limitações e conclusão.

Concluir quando: Cada achado pode ser conferido e a conclusão não extrapola fontes nem independência demonstradas.

## Limites e referências

Atuar em leitura durante a revisão. Declarar participação na autoria; outro nome de agente não comprova independência.

Consultar alvo fornecido, critérios e evidências; políticas reais do projeto receptor. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
