---
name: "ss-data-mapping"
description: "Mapear dados entre sistemas ou construir/corrigir transformações e pipelines."
---

# AG-07 — Data Integration

## Entradas

Schemas de origem/destino, amostras sanitizadas, frequência e regras de qualidade. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Mapear cada campo requerido a origem, tipo, nulidade, unidade e timezone. Identificar chaves e semântica de atualização.
2. Definir transformações e política para campo ausente, valor inválido e mudança de schema.
3. Tratar duplicatas, ordenação, reprocessamento e checkpoint; definir como reconciliar lote parcialmente aplicado.
4. Implementar transformação isolada ou produzir mapeamento quando só análise estiver autorizada, usando amostras sintéticas.
5. Conferir contagens, chaves, rejeições e invariantes do destino. Informar perdas, arredondamentos e casos sem regra definida.

## Saída e conclusão

Mapa de campos, transformação ou correção, política de rejeição/reprocessamento.

Concluir quando: Cada campo obrigatório tem regra explícita e falhas não são silenciosamente descartadas.

## Limites e referências

Sem credenciais em exemplos; acesso ou transferência de dados reais exige autorização.

Consultar schemas, dicionário de dados e amostras sanitizadas autorizadas. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
