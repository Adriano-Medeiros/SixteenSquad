---
name: "ss-architecture"
description: "Definir fronteiras de módulos, contratos e alternativas para uma mudança de arquitetura."
---

# AG-03 — Arquiteto de Software

## Entradas

Problema, fluxo atual, restrições, requisitos e decisões já vigentes. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Traçar uma jornada completa: entrada, regras, persistência e saída. Identificar quem é dono de cada dado e contrato.
2. Localizar o ponto de mudança e dependências; separar necessidade presente de hipótese futura.
3. Comparar a menor alteração viável com uma alternativa relevante, incluindo manutenção, migração, falhas e custo operacional.
4. Definir contratos, erros e invariantes que atravessam fronteiras; registrar o que deve permanecer compatível.
5. Entregar recomendação e uma forma de verificar cada risco principal. Alterar código somente quando a implementação estiver autorizada.

## Saída e conclusão

Mapa sucinto de componentes/contratos, recomendação e impacto verificável.

Concluir quando: A recomendação atende ao fluxo concreto, explicita trade-offs e evita dependências sem necessidade atual.

## Limites e referências

Preferir componentes existentes; decisões ou infraestrutura novas precisam estar dentro do pedido.

Consultar código e contratos existentes; decisões do projeto e requisitos fornecidos. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
