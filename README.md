# SixteenSquad

O **SixteenSquad Starter** reúne um Coordenador, 15 perfis de especialistas, 16 skills e templates para projetos no Codex. O [guia do Starter](starter/README.md) descreve os papéis, os limites e a adoção manual. Licença: [MIT](LICENSE).

## Instalação rápida

Abra o PowerShell 5.1 ou posterior em qualquer pasta e cole **este único comando**. Ele perguntará o caminho do projeto, mostrará os 35 arquivos e pedirá confirmação antes de instalá-los.

```powershell
& { param([string]$ProjectPath,[switch]$Preview) $url='https://raw.githubusercontent.com/Adriano-Medeiros/SixteenSquad/7c52a75cfe0874fb8745c88654d63c7a7e3b52cc/installer/install.ps1'; $sha='E9936D6BFE025464EB90AD7AE57C40BCA20D8B376CADD96870739EEE621970C3'; $file=Join-Path ([IO.Path]::GetTempPath()) ('sixteensquad-install-'+[guid]::NewGuid().ToString('N')+'.ps1'); try { [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $file; if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -ne $sha) { throw 'SHA-256 do instalador não confere; execução cancelada.' }; & $file -ProjectPath $ProjectPath -Preview:$Preview } finally { Remove-Item -LiteralPath $file -Force -ErrorAction SilentlyContinue } }
```

O URL aponta para o [commit publicado do instalador](https://github.com/Adriano-Medeiros/SixteenSquad/commit/7c52a75cfe0874fb8745c88654d63c7a7e3b52cc). O SHA-256 acima foi calculado dos bytes disponibilizados pelo GitHub. O comando não usa a branch mutável `main` para baixar o instalador e cancela a execução se o hash divergir.

O instalador obtém o pacote do [commit identificado](https://github.com/Adriano-Medeiros/SixteenSquad/commit/89ee03e32ac9cee56c1a38d815d93d44819ea799), mostra os arquivos, pergunta antes de copiar e não sobrescreve conteúdo divergente. Copia `AGENTS.md`, `.codex/agents/`, `.agents/skills/` e `templates/`. Não altera o README existente no projeto receptor. A opção `--preview` também é aceita ao chamar diretamente `installer/install.ps1`.

Os [testes do instalador](installer/tests/install.tests.ps1) cobrem ZIP inválido, conflitos, prévia, repetição, falhas de download e recuperação após erro de cópia. O comando não cria lançador permanente nem exige Git, Python ou Node.js.
