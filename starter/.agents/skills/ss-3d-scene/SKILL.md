---
name: "ss-3d-scene"
description: "Criar ou corrigir cenas, câmera, assets e interação 3D no projeto existente."
---

# AG-06 — 3D Developer

## Entradas

Engine/plataforma, cena-alvo, assets autorizados, interação e orçamento visual/desempenho. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Identificar engine, coordenadas, unidades e ciclo de vida da cena. Localizar câmera, luzes, objetos e recursos já usados.
2. Definir o menor fluxo observável: abrir cena, enquadrar objeto, interagir e sair. Registrar expectativas de escala, iluminação e seleção.
3. Reutilizar assets autorizados e checar materiais, transparência, colisões e limites de textura/geometria relevantes.
4. Implementar no escopo permitido e liberar recursos/eventos ao desmontar. Evitar criar objetos por frame sem necessidade.
5. Verificar comportamento no renderer disponível e medir quando autorizado. Sem renderização, relatar apenas inspeção estática, com ângulos/casos que faltam validar.

## Saída e conclusão

Cena/alteração delimitada ou especificação, critérios visuais e medições disponíveis.

Concluir quando: Cena tem escala/câmera coerentes, recursos com origem conhecida e resultado visual observado ou explicitamente pendente.

## Limites e referências

Não instalar engine, baixar assets ou presumir direitos de uso; confirmar unidades e formatos.

Consultar documentação da engine usada, cena e metadados dos assets do projeto. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
