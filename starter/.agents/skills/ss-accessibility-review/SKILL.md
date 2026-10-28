---
name: "ss-accessibility-review"
description: "Revisar ou corrigir barreiras de teclado, foco, semântica e conteúdo acessível."
---

# AG-16 — Accessibility Specialist

## Entradas

Tela/fluxo, tecnologias, público, critérios aplicáveis e ambiente de teste. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Identificar tarefas essenciais e elementos interativos; conferir nomes, papéis, estados e ordem semântica.
2. Examinar navegação por teclado, foco visível, ordem e retorno de foco em diálogos e conteúdo dinâmico.
3. Verificar rótulos, erros, instruções, alternativas de mídia, zoom/reflow, contraste e redução de movimento pertinentes.
4. Corrigir a menor barreira no escopo autorizado, preferindo elementos nativos e preservando comportamento.
5. Testar com teclado e tecnologia assistiva disponível quando autorizado; registrar navegador/ferramenta e separar leitura de código de teste real. Relacionar critério identificado sem inventar conformidade.

## Saída e conclusão

Barreiras localizadas, correções pertinentes e cobertura manual/automatizada declarada.

Concluir quando: Cada barreira tem localização, impacto na tarefa e verificação; limitações de cobertura ficam explícitas.

## Limites e referências

Não declarar conformidade integral a partir de inspeção parcial ou ferramenta automática.

Consultar interface, padrões do projeto e norma/versão aplicáveis quando fornecidas. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
