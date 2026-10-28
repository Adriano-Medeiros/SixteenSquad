---
name: "ss-frontend-states"
description: "Implementar ou revisar telas, componentes e integração frontend com estados assíncronos."
---

# AG-05 — Frontend Developer

## Entradas

Jornada, design disponível, API, componentes existentes e dispositivos-alvo. Se faltar informação que muda o resultado, explicitar a lacuna antes da ação dependente.

## Procedimento

1. Mapear carregamento, vazio, sucesso, erro e reenvio da ação; identificar estado de URL e estado local.
2. Reutilizar componentes e tokens existentes. Definir estrutura semântica, foco após ações e mensagens acessíveis.
3. Conectar dados preservando cancelamento/obsolescência de respostas e impedindo submissões duplicadas quando necessário.
4. Implementar apenas os estados e adaptações responsivas relevantes ao pedido; preservar entradas do usuário diante de falha.
5. Verificar navegação por teclado, tamanho de tela e erro de API pelos meios autorizados. Separar inspeção de código de teste em navegador.

## Saída e conclusão

Interface ou matriz de estados, comportamento verificável e limitações.

Concluir quando: Cada estado tem ação e feedback claros; interface não perde dados nem depende só de cor.

## Limites e referências

Reutilizar o design system; evitar alterações globais ou novas bibliotecas por conveniência.

Consultar design e contratos fornecidos, componentes, estilos e testes locais. Aplicam-se as [instruções do projeto](../../../AGENTS.md), o escopo do pedido e as permissões efetivas da sessão. A existência desta skill não amplia autorização.
