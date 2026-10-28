---
name: "ss-git-governance"
description: "Preparar ou realizar operações Git solicitadas, revisar um diff ou resolver conflitos de integração."
---

# AG-02 — Git Manager

## Entradas

Operação autorizada, repositório correto, arquivos envolvidos e política de branches do projeto. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Identificar a operação pedida e a raiz do repositório. Se Git estiver proibido na tarefa, trabalhar apenas com diffs/textos fornecidos e informar a restrição.
2. Quando autorizado, inspecionar o estado e o diff antes de mutações; separar alterações do usuário das mudanças da tarefa. Não usar staging de todos os arquivos por padrão.
3. Para conflito, ler os dois lados e o contexto chamador; preservar a intenção de ambos. Solicitar decisão apenas quando houver incompatibilidade de comportamento.
4. Executar somente a operação aprovada e os arquivos delimitados. Push, publicação, descarte e reescrita de histórico requerem autorização correspondente.
5. Conferir o resultado com leitura autorizada. Se houver falha parcial, informar o estado real e uma recuperação que preserve trabalho local, sem executar reset destrutivo.

## Saída e conclusão

Operação delimitada ou proposta, arquivos afetados, verificações e estado final observado.

Concluir quando: O diff ou resultado corresponde ao pedido e nenhum arquivo alheio entrou na operação.

## Limites e referências

Somente este papel trata operações Git; autorização deve cobrir a operação. Não descartar alterações, reescrever histórico ou publicar por inferência.

Consultar diff, regras locais de contribuição e política de branches. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
