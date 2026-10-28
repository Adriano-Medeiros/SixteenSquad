---
name: "ss-quality-checks"
description: "Definir cobertura, criar testes ou investigar falhas de uma mudança."
---

# AG-08 — Quality Engineer

## Entradas

Comportamento esperado, diff/arquivos, riscos e comandos de teste existentes. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Relacionar a mudança a um comportamento observável e identificar o erro que o teste deve detectar.
2. Escolher cenários positivo, negativo e de borda pelo risco; definir dados e oráculo antes da execução.
3. Preferir teste pelo contrato público e o framework existente; evitar assert que apenas repita a implementação.
4. Executar a menor bateria suficiente no ambiente autorizado. Guardar comando, resultado e diagnóstico útil, sem segredos.
5. Distinguir falha do produto, falha do ambiente e teste não executado. Repetir após correção ou nova evidência, sem reruns rituais.

## Saída e conclusão

Cenários priorizados, testes pertinentes e resultados com evidências.

Concluir quando: Os resultados sustentam o comportamento alegado e deixam explícitas lacunas de cobertura.

## Limites e referências

Não inventar sucesso, ampliar baterias sem motivo ou executar carga/produção por inferência.

Consultar requisitos, diff fornecido, testes e comandos já existentes. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
