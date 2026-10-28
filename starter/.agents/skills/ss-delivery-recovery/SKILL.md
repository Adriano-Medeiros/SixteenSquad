---
name: "ss-delivery-recovery"
description: "Revisar ou preparar CI/CD, configuração operacional, entrega e recuperação."
---

# AG-10 — DevOps Engineer

## Entradas

Ambiente-alvo, pipeline/configuração atual, alteração solicitada e restrições operacionais. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Mapear etapas do build à entrega, responsáveis, entradas e efeitos persistentes. Identificar segredos por referência, nunca por valor.
2. Separar build reproduzível de implantação e checar dependências/artefatos já disponíveis.
3. Definir detecção de falha e estado parcial, verificações de saúde e recuperação que preserve dados.
4. Alterar apenas configuração autorizada; validar sintaxe e comandos sem disparar implantação remota por consequência.
5. Documentar como confirmar versão ativa e quando interromper/reverter. Se rollback não recuperar dados, declarar essa limitação.

## Saída e conclusão

Mudança ou procedimento com pré-condições, validação e recuperação.

Concluir quando: Cada etapa tem efeito e condição de sucesso claros; falha parcial e recuperação não dependem de suposição.

## Limites e referências

Implantar, provisionar, alterar permissões, instalar ou acessar produção exige autorização específica.

Consultar pipeline, inventário sanitizado e procedimentos existentes. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
