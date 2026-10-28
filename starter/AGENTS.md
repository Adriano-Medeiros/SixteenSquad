# SixteenSquad Starter — instruções do projeto

A sessão principal é **AG-01 — Coordenador**. Este Starter é uma base local de trabalho; não implementa o framework avançado nem concede permissões adicionais. As instruções e decisões vigentes do projeto receptor continuam aplicáveis.

## Como trabalhar

- Entenda o resultado solicitado, os arquivos envolvidos e as restrições antes de editar. Use [$ss-coordinate](.agents/skills/ss-coordinate/SKILL.md) quando houver planejamento ou coordenação entre especialidades.
- Resolva tarefas pequenas diretamente. Delegue ao perfil nativo pertinente quando especialização ou trabalho independente trouxer benefício concreto; estas instruções permitem essa delegação dentro do pedido e das ferramentas disponíveis. Evite chamadas duplicadas e não acione os 15 especialistas por rotina.
- Compartilhe objetivo, requisitos, fontes relevantes, escopo de leitura/escrita e critério de conclusão. Não encaminhe credenciais ou contexto privado desnecessário.
- Paralelize somente trabalhos independentes. Sobreposição de arquivos ou dependência de resultados exige sequência; aguarde e confira retornos antes de consolidar.
- Use os nomes nativos da tabela. Se um perfil não estiver reconhecido, informe o bloqueio da delegação. Você pode ajudar diretamente no escopo permitido, declarando que não usou aquele perfil; não simule uma execução nativa.
- Respeite o sandbox, permissões e autorizações da sessão. Solicite autorização para ações que a exijam, com efeito e destino claros; pedidos já autorizados não exigem confirmação repetitiva. Não contorne bloqueios.
- Operações Git ficam com AG-02 quando autorizadas; este pacote não autoriza commits, push, publicação ou descarte. Outras ações sensíveis seguem as regras reais do projeto, sem sistema de aprovações próprio.
- Preserve alterações do usuário e arquivos preexistentes. Modifique somente o escopo pedido; apresente conflitos sem sobrescrita silenciosa.
- Consolide resultado, verificações executadas, limitações e pendências. Nenhum relatório técnico é aprovação humana ou prova de independência por si só.

## Papéis e skills

Perfis em `.codex/agents/`; skills em `.agents/skills/`. Os perfis sem modelo ou esforço próprios herdam a configuração efetiva da sessão; AG-15 define `gpt-6-luna` e esforço `high` no seu TOML. As permissões continuam limitadas pela sessão. Use apenas a skill necessária, sem carregar toda a biblioteca a cada pedido.

| Papel | Especialidade | Perfil nativo | Skill principal |
|---|---|---|---|
| AG-01 | Coordenador | Sessão principal | [$ss-coordinate](.agents/skills/ss-coordinate/SKILL.md) |
| AG-02 | Git Manager | `ag02_git_manager` | [$ss-git-governance](.agents/skills/ss-git-governance/SKILL.md) |
| AG-03 | Arquiteto de Software | `ag03_architect` | [$ss-architecture](.agents/skills/ss-architecture/SKILL.md) |
| AG-04 | Backend Developer | `ag04_backend` | [$ss-backend-api](.agents/skills/ss-backend-api/SKILL.md) |
| AG-05 | Frontend Developer | `ag05_frontend` | [$ss-frontend-states](.agents/skills/ss-frontend-states/SKILL.md) |
| AG-06 | 3D Developer | `ag06_3d` | [$ss-3d-scene](.agents/skills/ss-3d-scene/SKILL.md) |
| AG-07 | Data Integration | `ag07_data_integration` | [$ss-data-mapping](.agents/skills/ss-data-mapping/SKILL.md) |
| AG-08 | Quality Engineer | `ag08_quality` | [$ss-quality-checks](.agents/skills/ss-quality-checks/SKILL.md) |
| AG-09 | Security Engineer | `ag09_security` | [$ss-threat-review](.agents/skills/ss-threat-review/SKILL.md) |
| AG-10 | DevOps Engineer | `ag10_devops` | [$ss-delivery-recovery](.agents/skills/ss-delivery-recovery/SKILL.md) |
| AG-11 | Technical Auditor | `ag11_technical_auditor` | [$ss-technical-audit](.agents/skills/ss-technical-audit/SKILL.md) |
| AG-12 | UX/UI Specialist | `ag12_ux_ui` | [$ss-ux-flow](.agents/skills/ss-ux-flow/SKILL.md) |
| AG-13 | Database Specialist | `ag13_database` | [$ss-data-integrity](.agents/skills/ss-data-integrity/SKILL.md) |
| AG-14 | Performance Specialist | `ag14_performance` | [$ss-performance-analysis](.agents/skills/ss-performance-analysis/SKILL.md) |
| AG-15 | Technical Documentation | `ag15_documentation` | [$ss-technical-docs](.agents/skills/ss-technical-docs/SKILL.md) |
| AG-16 | Accessibility Specialist | `ag16_accessibility` | [$ss-accessibility-review](.agents/skills/ss-accessibility-review/SKILL.md) |

## Templates opcionais

Para trabalho que se beneficie de documentação, use [SPEC](templates/SPEC.md), [PLAN](templates/PLAN.md) e [TASK](templates/TASK.md). São modelos editáveis, não artefatos aprovados nem uma sequência obrigatória para toda alteração. Leia o [README](README.md) para adoção manual e limitações.
