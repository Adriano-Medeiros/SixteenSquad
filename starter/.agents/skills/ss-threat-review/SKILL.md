---
name: "ss-threat-review"
description: "Analisar segurança de um fluxo, permissões, entrada não confiável ou mudança de autenticação."
---

# AG-09 — Security Engineer

## Entradas

Ativos, atores, fluxos, fronteiras de confiança e controles existentes. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Identificar o ativo protegido e o que cada ator pode fazer; separar instruções de controles técnicos efetivos.
2. Traçar entrada não confiável até ações sensíveis, incluindo ferramentas, rede, arquivos e autorização por objeto.
3. Examinar abuso concreto: elevação de privilégio, injeção, exposição, replay ou bypass conforme o fluxo realmente existente.
4. Para cada achado, mostrar condição necessária, trecho/evidência, impacto e menor mitigação viável; diferenciar hipótese de vulnerabilidade demonstrada.
5. Propor verificação negativa com dados sintéticos; executar apenas se explicitamente no escopo autorizado. Registrar risco residual.

## Saída e conclusão

Achados priorizados com ameaça, evidência, impacto e mitigação.

Concluir quando: Cada risco aponta uma fronteira e evidência específica; não há alegação de segurança integral por ausência de achados.

## Limites e referências

Revisão não autoriza exploração ativa, leitura de segredos, varredura ou teste contra terceiros.

Consultar código/configuração sanitizada, modelo de acesso e requisitos de segurança do projeto. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
