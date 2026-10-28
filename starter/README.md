# SixteenSquad Starter

Base local e reutilizável para trabalhar no Codex com um Coordenador, quinze perfis de especialistas e dezesseis skills. Copie para a raiz de um projeto e use os componentes necessários ao pedido. Não há servidor, banco, orquestrador próprio, instalação global ou comando `sixteensquad install`.

Esta entrega é separada da implementação avançada da SPEC-0002. Não conclui suas pendências, gates ou aprovações e não transporta autorizações de um projeto para outro. Os templates são exemplos editáveis, não SPECs/PLANs/TASKs oficiais.

## Conteúdo

```text
starter/
├── AGENTS.md
├── README.md
├── VALIDATION.md
├── .codex/
│   └── agents/              # 15 perfis TOML, AG-02 a AG-16
├── .agents/
│   └── skills/              # 16 pastas, cada uma com SKILL.md
├── templates/
│   ├── SPEC.md
│   ├── PLAN.md
│   └── TASK.md
└── tools/
    ├── validate_starter.py  # validação local, somente leitura
    └── tests/              # regressões com unittest e dados descartáveis
```

## Papéis e skills disponíveis

Cada perfil tem responsabilidades, entradas, saída, limites e acionamento, além de referência à skill principal. Skills podem ser compartilhadas quando pertinentes; dezesseis é o conjunto inicial, não um teto.

| Papel | Perfil / instruções | Skill principal |
|---|---|---|
| AG-01 — Coordenador | [AGENTS.md](AGENTS.md) — principal | [$ss-coordinate](.agents/skills/ss-coordinate/SKILL.md) |
| AG-02 — Git Manager | [ag02_git_manager](.codex/agents/ag02_git_manager.toml) | [$ss-git-governance](.agents/skills/ss-git-governance/SKILL.md) |
| AG-03 — Arquiteto de Software | [ag03_architect](.codex/agents/ag03_architect.toml) | [$ss-architecture](.agents/skills/ss-architecture/SKILL.md) |
| AG-04 — Backend Developer | [ag04_backend](.codex/agents/ag04_backend.toml) | [$ss-backend-api](.agents/skills/ss-backend-api/SKILL.md) |
| AG-05 — Frontend Developer | [ag05_frontend](.codex/agents/ag05_frontend.toml) | [$ss-frontend-states](.agents/skills/ss-frontend-states/SKILL.md) |
| AG-06 — 3D Developer | [ag06_3d](.codex/agents/ag06_3d.toml) | [$ss-3d-scene](.agents/skills/ss-3d-scene/SKILL.md) |
| AG-07 — Data Integration | [ag07_data_integration](.codex/agents/ag07_data_integration.toml) | [$ss-data-mapping](.agents/skills/ss-data-mapping/SKILL.md) |
| AG-08 — Quality Engineer | [ag08_quality](.codex/agents/ag08_quality.toml) | [$ss-quality-checks](.agents/skills/ss-quality-checks/SKILL.md) |
| AG-09 — Security Engineer | [ag09_security](.codex/agents/ag09_security.toml) | [$ss-threat-review](.agents/skills/ss-threat-review/SKILL.md) |
| AG-10 — DevOps Engineer | [ag10_devops](.codex/agents/ag10_devops.toml) | [$ss-delivery-recovery](.agents/skills/ss-delivery-recovery/SKILL.md) |
| AG-11 — Technical Auditor | [ag11_technical_auditor](.codex/agents/ag11_technical_auditor.toml) | [$ss-technical-audit](.agents/skills/ss-technical-audit/SKILL.md) |
| AG-12 — UX/UI Specialist | [ag12_ux_ui](.codex/agents/ag12_ux_ui.toml) | [$ss-ux-flow](.agents/skills/ss-ux-flow/SKILL.md) |
| AG-13 — Database Specialist | [ag13_database](.codex/agents/ag13_database.toml) | [$ss-data-integrity](.agents/skills/ss-data-integrity/SKILL.md) |
| AG-14 — Performance Specialist | [ag14_performance](.codex/agents/ag14_performance.toml) | [$ss-performance-analysis](.agents/skills/ss-performance-analysis/SKILL.md) |
| AG-15 — Technical Documentation | [ag15_documentation](.codex/agents/ag15_documentation.toml) | [$ss-technical-docs](.agents/skills/ss-technical-docs/SKILL.md) |
| AG-16 — Accessibility Specialist | [ag16_accessibility](.codex/agents/ag16_accessibility.toml) | [$ss-accessibility-review](.agents/skills/ss-accessibility-review/SKILL.md) |

Os procedimentos aproveitam as especialidades e gatilhos da matriz de agentes/skills v0.2 existente no SixteenSquad. A base é autossuficiente: não exige copiar a matriz, decisões, relatórios ou outros documentos do framework avançado. Ações reais dependem do pedido e das permissões do projeto receptor.

## Abrir e usar no Codex

1. Abra a pasta **starter** como projeto/pasta de trabalho no desktop, ou a raiz do novo projeto para o qual você copiou a base. Abrir somente a pasta ancestral não garante descoberta desses componentes locais.
2. Inicie uma conversa nesse projeto. Na CLI, entre nessa pasta e execute `codex`, usando a instalação e a conta já disponíveis. Este pacote não instala nem autentica o Codex.
3. Peça uma tarefa concreta. O Coordenador pode resolver tarefas pequenas diretamente e delegar especialidades quando necessário.
4. Para testar a delegação deliberadamente, use o nome exato, por exemplo: “Delegue uma revisão somente de leitura deste README ao perfil nativo ag15_documentation. Use ss-technical-docs e retorne apenas achados. Se o perfil não for reconhecido, informe isso.”
5. Para uma skill na CLI, use `$ss-coordinate` ou selecione via `/skills`. No aplicativo, use o seletor de skills disponível. Se arquivos novos não aparecerem, reabra a sessão/aplicativo; não altere configuração global como tentativa automática.

Exemplos de pedidos:

- “Use $ss-coordinate para dividir a implementação deste formulário entre as especialidades necessárias.”
- “Use $ss-backend-api para revisar validação e autorização deste endpoint, sem editar.”
- “Delegue a ag16_accessibility a revisão somente de leitura dos estados deste formulário.”

Disponibilidade de arquivo, declaração textual e resposta correta não são, sozinhas, prova de seleção nativa. Confira a atividade/ferramenta de delegação e a origem da skill quando a superfície oferecer essa informação. A leitura manual do SKILL.md é útil, mas não deve ser anunciada como reconhecimento nativo.

## Copiar manualmente para um projeto novo

1. Escolha a pasta de destino e confira o que já existe, inclusive arquivos ocultos. Esta entrega não modifica outro projeto.
2. Copie **o conteúdo interno** necessário do Starter para a raiz do destino: AGENTS.md, os arquivos de `.codex/agents/`, as pastas de `.agents/skills/` e, se úteis, `templates/` e `tools/`.
3. Preserve todos os arquivos preexistentes. Se houver AGENTS.md, compare e incorpore manualmente apenas as orientações desejadas; respeite instruções e decisões do receptor.
4. Em conflito de perfil ou skill, pare e escolha conscientemente: manter a versão existente ou criar uma variante com novo nome, atualizando arquivo, campo `name`, referências e tabela. Não substituir silenciosamente nem deixar nomes duplicados.
5. Não copie a pasta pessoal `.codex`, configurações de conta, credenciais, históricos, permissões ou documentos do projeto de origem. A base contém somente `.codex/agents`, sem config.toml.
6. Abra o destino no Codex e confira os componentes reconhecidos antes de depender deles. Permissões, recursos e restrições pertencem à sessão e ao projeto receptor.

Não há script de cópia, sincronização, instalação ou atualização de terceiros. A validação local abaixo não autoriza editar o destino nem resolve conflitos por conta própria.

## Adicionar agentes e skills

Para outro especialista, crie um TOML com nome único em `.codex/agents/` e os campos `name`, `description` e `developer_instructions`. Descreva gatilho, entradas, responsabilidade, resultado e limites; aponte para a skill aplicável. Preserve o Coordenador na sessão principal. Atualize a tabela e ajuste a expectativa de quantidade no validador se ampliar o catálogo.

Para outra skill, crie `.agents/skills/nome-da-skill/SKILL.md` com front matter YAML contendo nome e descrição de acionamento, seguido de procedimento, entradas, saída, referências e critério de conclusão. Esta base usa duas chaves com valores textuais entre aspas JSON, compatíveis com YAML, para permitir validação sem dependência adicional. Reutilize skill existente quando o procedimento já atender ao papel.

Os perfis sem configuração própria de modelo/esforço herdam a configuração efetiva da sessão. A exceção atual é **AG-15**, cujo TOML define `model = "gpt-6-luna"` e `model_reasoning_effort = "high"`. Os demais perfis não fixam esses campos. A frase geral sobre herança em AGENTS.md deve ser lida considerando essa configuração explícita do AG-15. Instruções de papel não criam isolamento de sistema operacional nem ampliam permissões.

## Validação e limitações locais

A validação pode ser reproduzida com **Python 3.11 ou posterior já disponível**:

```powershell
python -X utf8 -B -m unittest discover -s tools/tests -v
python -X utf8 -B tools/validate_starter.py
```

Esse runtime é opcional para conferir o pacote, não para o Codex ler perfis e skills. O validador usa somente a biblioteca padrão, verifica TOML, o subconjunto YAML adotado, cobertura, associações com a tabela canônica de AGENTS.md e links locais, e busca alguns padrões de credenciais. O validador não escreve arquivos, instala componentes ou executa Git. Os testes criam e removem apenas diretórios temporários descartáveis dentro de `tools/tests/`; execute os dois comandos sequencialmente. A busca de padrões não certifica ausência de todo segredo.

Resultados atuais, verificados em **2026-10-28**; `VALIDATION.md` permanece como registro histórico da entrega inicial:

- Validador: **`ok: true`, 15 perfis, 16 skills, 73 links locais e nenhum erro**. Agora aceita os campos opcionais do AG-15, mantém os três campos essenciais obrigatórios e produz erros controlados para TOML/YAML inválidos e tipos incorretos.
- Suíte: **41 testes, 39 aprovados e dois ignorados**, sem falhas, na execução autorizada fora do sandbox. Os dois ignorados requerem criação de symlink de arquivo/diretório, indisponível com os privilégios Windows atuais (`WinError 1314`). Não houve alteração de privilégios ou configuração do sistema.
- Junction e hard link reais, apontando para sentinelas sintéticos fora da raiz temporária validada, foram recusados sem leitura desses sentinelas. A recusa por atributo de reparse point também foi exercitada com simulação controlada da resposta do sistema. Isso não substitui os dois testes reais de symlink pendentes. Na execução intermediária de 40 testes dentro do sandbox, junction e hard link também foram bloqueados na criação: 36 testes passaram e quatro foram ignorados.
- UNC e tentativas de escape foram testados sintaticamente, proibindo por mocks abertura, consulta de existência e resolução de destinos. Não houve consulta a compartilhamento de rede. Erros de permissão e leitura são falhas da validação, não sucesso silencioso.
- Na entrega inicial, a CLI observada foi **codex-cli 0.165.0-alpha.1.2**; sua consulta de reconhecimento ficou bloqueada pelo sandbox. Isso não invalida os testes posteriores no aplicativo descritos abaixo. A versão da CLI não foi novamente consultada nesta correção.
- Em **2026-10-27**, na conversa local **“Verificar modelos e esforço”**, os registros de sessão identificaram `ag15_documentation` com `gpt-6-luna` / `high`, `ag08_quality` e `ag09_security` com `gpt-6-astra` / `high`. Houve leitura observada de `ss-technical-docs`, `ss-quality-checks` e `ss-threat-review`, respectivamente. AG-08 e AG-09 analisaram a versão anterior do validador em sessões concorrentes. Esses testes não são uma revisão das correções atuais; a tentativa de retomá-los nesta etapa foi recusada pelo aplicativo por serem instâncias descarregadas.
- Os testes nativos estão comprovados no nível dos registros locais (`agent_role`, `turn_context` e retornos de ferramentas), não por autodeclaração. Não comprovam a identidade interna do modelo servido nem cobertura funcional dos 16 papéis. Outros perfis, skills e o comportamento na sessão receptora continuam pendentes; não declarar “16/16 funcionais”.
- Python disponível nesta execução: **3.12.14** do runtime já fornecido pelo Codex; PyYAML ausente. O validador geral `quick_validate.py` da skill-creator não foi executado por depender de PyYAML. Nenhuma dependência foi instalada.
- O YAML aceito continua restrito a `name` e `description` com strings entre aspas JSON; delimitadores são linhas inteiras `---`, permitindo essa sequência dentro de descrições. Não é um parser YAML geral. Campos opcionais TOML são aceitos; `model` e `model_reasoning_effort` precisam ser textos não vazios. A disponibilidade do modelo e o schema nativo completo dependem do cliente Codex.
- Links inline, imagens, referências, títulos, escapes, caminhos percent-encoded e âncoras Markdown comuns são conferidos; exemplos de código são ignorados. Não é implementação completa de CommonMark/HTML nem verificador de URLs externas. Âncoras em alvos não Markdown são reportadas como não verificáveis.
- Caminhos são comparados lexicalmente com um inventário seguro: links documentais não causam consultas de arquivos. Por cautela, o inventário recusa todos os symlinks/junctions/reparse points e arquivos com hard links, inclusive internos, e limita cada texto a 2 MiB. No Windows abre os objetos sem seguir reparse points e mantém ancestrais abertos sem compartilhar escrita/exclusão; indisponibilidade dessas aberturas gera erro. Isso não é sandbox contra administrador, nem snapshot atômico de toda a árvore. A implementação POSIX não foi executada neste ambiente Windows.
- Clientes/versões podem diferir em recursos e visibilidade. A base não configura MCP, modelo, sandbox ou permissões globais.

## Fontes do formato

Consultadas em **2026-10-27**; documentação mutável:

- [Agentes personalizados do Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents): arquivos TOML por projeto, campos obrigatórios e herança.
- [Skills do Codex](https://learn.chatgpt.com/docs/build-skills): SKILL.md e descoberta local em `.agents/skills`.
- [Referência de configuração](https://learn.chatgpt.com/docs/config-file/config-reference): referência complementar; nenhuma configuração global foi criada.

Os procedimentos especializados são instruções próprias do Starter, não cópias de manuais nem implementação das capacidades avançadas do framework.
