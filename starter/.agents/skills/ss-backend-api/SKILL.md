---
name: "ss-backend-api"
description: "Projetar, implementar ou corrigir endpoints, serviços e regras de negócio de backend."
---

# AG-04 — Backend Developer

## Entradas

Caso de uso, contrato da API, regras de domínio, persistência e autorização disponível. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Seguir uma requisição do transporte até a regra e persistência. Confirmar autenticação e autorização por recurso, não só presença de token.
2. Definir tipos, campos obrigatórios, limites, códigos de erro e compatibilidade com consumidores existentes.
3. Tratar duplicatas/idempotência e fronteiras de transação quando a operação muda estado; evitar retorno de sucesso antes de efeitos confirmados.
4. Implementar a menor mudança no padrão do projeto quando autorizado, preservando dados sensíveis fora de logs e respostas.
5. Verificar caminho positivo, entrada inválida, acesso negado e falha de dependência com ferramentas já disponíveis. Declarar o que não foi executado.

## Saída e conclusão

Contrato ou alteração focalizada, tratamento de falhas e verificações pertinentes.

Concluir quando: A regra é observável pelo contrato, erros são consistentes e testes relevantes não dependem de dados de produção.

## Limites e referências

Não chamar produção, alterar dados reais ou introduzir dependências sem autorização.

Consultar contratos da API, esquemas, chamadas existentes e testes do projeto. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
