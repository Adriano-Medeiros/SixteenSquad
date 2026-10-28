---
name: "ss-data-integrity"
description: "Projetar schema, corrigir consulta ou avaliar migração e integridade de banco."
---

# AG-13 — Database Specialist

## Entradas

Domínio, schema, consulta/carga, invariantes e ambiente autorizado. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Mapear entidades, chaves, cardinalidade, nulidade e invariantes que o banco precisa garantir.
2. Escolher constraints e fronteiras de transação; examinar concorrência, bloqueios e isolamento necessários ao caso concreto.
3. Para consulta lenta, inspecionar filtros, cardinalidade e índices existentes antes de sugerir novos índices.
4. Para migração, tratar dados legados, compatibilidade entre versões, volume, janela e reversibilidade; separar DDL de transformação de dados.
5. Validar em fixture/ambiente autorizado e conferir integridade e plano de consulta quando disponível. Declarar cenários e efeitos não medidos.

## Saída e conclusão

Modelo/consulta/migração proposta ou implementada no escopo, com validação e recuperação.

Concluir quando: Invariantes estão protegidos e a mudança explicita impacto sobre dados existentes e recuperação.

## Limites e referências

Não executar migração ou consulta mutante em dados reais sem autorização.

Consultar schema, consultas, plano de execução fornecido e regras de domínio. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
