# SixteenSquad CLI

Instalador por projeto para o SixteenSquad Starter no Codex.

```powershell
# Dentro do projeto
npx sixteensquad@latest install starter

# Instalando em outro diretório
npx sixteensquad@latest install starter "C:\MEU_PROJETO"

# Prévia (não modifica o destino)
npx sixteensquad@latest install starter --preview
```

O pacote npm leva os 35 arquivos do Starter distribuídos junto com a CLI; após o download pelo npm, não faz outra solicitação ao GitHub. Exibe os arquivos, pede confirmação, nunca sobrescreve arquivos divergentes e ignora arquivos idênticos. Não modifica configurações globais e não instala nenhum serviço.

Código-fonte e licença MIT: https://github.com/Adriano-Medeiros/SixteenSquad
