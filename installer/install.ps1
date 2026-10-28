param(
    [string]$ProjectPath,
    [switch]$Preview,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Remaining
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$PackageCommit = '89ee03e32ac9cee56c1a38d815d93d44819ea799'
$ArchiveUrl = "https://codeload.github.com/Adriano-Medeiros/SixteenSquad/zip/$PackageCommit"
if ($ProjectPath -eq '--preview') { $ProjectPath = ''; $Preview = $true }
foreach ($argument in $Remaining) {
    if ($argument -eq '--preview') { $Preview = $true }
    else { throw "Argumento desconhecido: $argument" }
}

function Assert-ArchiveName([string]$Name) {
    if (-not $Name -or $Name.StartsWith('/') -or $Name.Contains('\') -or
        $Name -match '[\x00-\x1f\x7f:]' -or $Name -match '(^|/)(\.|\.\.)($|/)' -or
        $Name -match '(^|/)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|/|$)' -or
        $Name -match '//|[<>"|?*]' -or $Name -match '[. ](/|$)') {
        throw "Entrada ZIP perigosa: $Name"
    }
}

function Assert-SafeDestination([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { throw 'Caminho do projeto vazio.' }
    $full = [IO.Path]::GetFullPath($Path)
    if ($full.StartsWith('\\')) { throw 'Destino UNC não é aceito.' }
    $cursor = [IO.Path]::GetPathRoot($full)
    foreach ($part in $full.Substring($cursor.Length).Split([IO.Path]::DirectorySeparatorChar)) {
        if (-not $part) { continue }
        $cursor = Join-Path $cursor $part
        $item = Get-Item -LiteralPath $cursor -Force -ErrorAction SilentlyContinue
        if ($null -ne $item) {
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Destino contém link/junction: $cursor"
            }
            if (-not $item.PSIsContainer) { throw "Destino contém arquivo no lugar de pasta: $cursor" }
        }
    }
    return $full
}

function Get-OfficialArchive([string]$Uri, [string]$OutputPath) {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $request = [Net.HttpWebRequest]::Create($Uri)
    $request.Timeout = 30000
    $request.ReadWriteTimeout = 30000
    $response = $request.GetResponse()
    try {
        if ($response.ResponseUri.Host -ne 'codeload.github.com') { throw 'Download redirecionado para host inesperado.' }
        if ($response.ContentLength -gt 16MB) { throw 'ZIP excede 16 MiB.' }
        $inputStream = $response.GetResponseStream()
        try {
            $outputStream = [IO.File]::Open($OutputPath, [IO.FileMode]::CreateNew)
            try {
                $buffer = New-Object byte[] 65536
                $received = [long]0
                while (($count = $inputStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
                    $received += $count
                    if ($received -gt 16MB) { throw 'ZIP excede 16 MiB.' }
                    $outputStream.Write($buffer, 0, $count)
                }
            }
            finally { $outputStream.Dispose() }
        }
        finally { $inputStream.Dispose() }
    }
    finally { $response.Dispose() }
}

function Read-StarterArchive([string]$ZipPath, [string]$StagePath, [string]$Commit) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [IO.Compression.ZipFile]::OpenRead($ZipPath)
    $prefix = "SixteenSquad-$Commit/starter/"
    $selected = New-Object 'System.Collections.Generic.Dictionary[string,string]' ([StringComparer]::OrdinalIgnoreCase)
    $seen = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
        $total = [long]0
    try {
        if ($zip.Entries.Count -gt 1000) { throw 'ZIP contém entradas demais.' }
        foreach ($entry in $zip.Entries) {
            $name = $entry.FullName
            $checkedName = if ($name.EndsWith('/')) { $name.Substring(0, $name.Length - 1) } else { $name }
            Assert-ArchiveName $checkedName
            if (-not $seen.Add($name)) { throw "Entrada ZIP duplicada: $name" }
            $unixMode = ($entry.ExternalAttributes -shr 16) -band 0xF000
            if ($unixMode -eq 0xA000 -or ($entry.ExternalAttributes -band 0x400)) {
                throw "Link ou reparse point no ZIP: $name"
            }
            if ($name.EndsWith('/')) { continue }
            if (-not $name.StartsWith($prefix, [StringComparison]::Ordinal)) { continue }
            $relative = $name.Substring($prefix.Length)
            $allowed = $relative -eq 'AGENTS.md' -or
                $relative -match '^\.codex/agents/ag(0[2-9]|1[0-6])_[a-z0-9_]+\.toml$' -or
                $relative -match '^\.agents/skills/ss-[a-z0-9-]+/SKILL\.md$' -or
                $relative -match '^templates/(SPEC|PLAN|TASK)\.md$'
            if (-not $allowed) { continue }
            if ($entry.Length -gt 2MB) { throw "Arquivo excede 2 MiB: $relative" }
            $target = Join-Path $StagePath ($relative.Replace('/', [IO.Path]::DirectorySeparatorChar))
            $parent = Split-Path -Parent $target
            [IO.Directory]::CreateDirectory($parent) | Out-Null
            $inputStream = $entry.Open()
            try {
                $outputStream = [IO.File]::Open($target, [IO.FileMode]::CreateNew)
                try {
                    $buffer = New-Object byte[] 65536
                    $written = [long]0
                    while (($count = $inputStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
                        $written += $count
                        if ($written -gt 2MB -or ($total + $written) -gt 8MB -or $written -gt $entry.Length) {
                            throw "Entrada ZIP excede limites declarados: $relative"
                        }
                        $outputStream.Write($buffer, 0, $count)
                    }
                    if ($written -ne $entry.Length) { throw "Entrada ZIP truncada: $relative" }
                    $total += $written
                }
                finally { $outputStream.Dispose() }
            }
            finally { $inputStream.Dispose() }
            $selected.Add($relative, $target)
        }
        $profiles = @($selected.Keys | Where-Object { $_ -like '.codex/agents/*.toml' })
        $skills = @($selected.Keys | Where-Object { $_ -like '.agents/skills/*/SKILL.md' })
        $templates = @($selected.Keys | Where-Object { $_ -like 'templates/*.md' })
        if ($selected.Count -ne 35 -or -not $selected.ContainsKey('AGENTS.md') -or
            $profiles.Count -ne 15 -or $skills.Count -ne 16 -or $templates.Count -ne 3) {
            throw 'Pacote incompleto ou composição inesperada (esperados 35 arquivos).'
        }
        return $selected
    }
    finally { $zip.Dispose() }
}

function Get-PendingFiles([string]$Destination, $Files) {
    $pending = New-Object 'System.Collections.Generic.Dictionary[string,string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($relative in $Files.Keys) {
        $target = Join-Path $Destination ($relative.Replace('/', [IO.Path]::DirectorySeparatorChar))
        $parent = Split-Path -Parent $target
        while ($parent -and $parent.StartsWith($Destination, [StringComparison]::OrdinalIgnoreCase)) {
            $item = Get-Item -LiteralPath $parent -Force -ErrorAction SilentlyContinue
            if ($null -ne $item) {
                if (-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
                    throw "Pasta de destino insegura: $parent"
                }
            }
            if ($parent -eq $Destination) { break }
            $parent = Split-Path -Parent $parent
        }
        $item = Get-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue
        if ($null -ne $item) {
            if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
                (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne
                (Get-FileHash -LiteralPath $Files[$relative] -Algorithm SHA256).Hash) {
                throw "Conflito: $target já existe com conteúdo diferente ou tipo inseguro."
            }
        }
        else { $pending.Add($relative, $Files[$relative]) }
    }
    return $pending
}

function Install-StagedFiles([string]$Destination, $Files) {
    $createdFiles = New-Object 'System.Collections.Generic.List[string]'
    $createdDirs = New-Object 'System.Collections.Generic.List[string]'
    try {
        $dirs = @()
        $cursor = [IO.Path]::GetPathRoot($Destination)
        foreach ($part in $Destination.Substring($cursor.Length).Split([IO.Path]::DirectorySeparatorChar)) {
            if ($part) { $cursor = Join-Path $cursor $part; $dirs += $cursor }
        }
        foreach ($relative in $Files.Keys) {
            $parent = Split-Path -Parent (Join-Path $Destination ($relative.Replace('/', [IO.Path]::DirectorySeparatorChar)))
            while ($parent -and $parent.StartsWith($Destination, [StringComparison]::OrdinalIgnoreCase) -and $parent -notin $dirs) {
                $dirs += $parent
                if ($parent -eq $Destination) { break }
                $parent = Split-Path -Parent $parent
            }
        }
        foreach ($dir in ($dirs | Sort-Object Length, { $_ })) {
            if ($null -eq (Get-Item -LiteralPath $dir -Force -ErrorAction SilentlyContinue)) {
                [IO.Directory]::CreateDirectory($dir) | Out-Null
                $createdDirs.Add($dir)
            }
        }
        foreach ($relative in ($Files.Keys | Sort-Object)) {
            $target = Join-Path $Destination ($relative.Replace('/', [IO.Path]::DirectorySeparatorChar))
            $source = [IO.File]::OpenRead($Files[$relative])
            try {
                $output = [IO.File]::Open($target, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
                $createdFiles.Add($target)
                try { $source.CopyTo($output) }
                finally { $output.Dispose() }
            }
            finally { $source.Dispose() }
        }
    }
    catch {
        foreach ($file in $createdFiles) { try { [IO.File]::Delete($file) } catch { Write-Warning "Reversão falhou: $file" } }
        foreach ($dir in ($createdDirs | Sort-Object Length -Descending)) { try { [IO.Directory]::Delete($dir) } catch { Write-Warning "Reversão falhou: $dir" } }
        throw
    }
}

function Invoke-SixteenSquadInstall([string]$Destination, [switch]$DryRun) {
    if ([string]::IsNullOrWhiteSpace($Destination)) { $Destination = Read-Host 'Caminho completo do projeto' }
    $full = Assert-SafeDestination $Destination
    $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    $temp = Join-Path $tempRoot ('sixteensquad-' + [guid]::NewGuid().ToString('N'))
    [IO.Directory]::CreateDirectory($temp) | Out-Null
    try {
        $zip = Join-Path $temp 'source.zip'
        $stage = Join-Path $temp 'stage'
        [IO.Directory]::CreateDirectory($stage) | Out-Null
        Get-OfficialArchive $ArchiveUrl $zip
        $files = Read-StarterArchive $zip $stage $PackageCommit
        $pending = Get-PendingFiles $full $files
        Write-Host "Origem: SixteenSquad $PackageCommit"
        Write-Host "Destino: $full"
        Write-Host "Arquivos do pacote: $($files.Count); já idênticos: $($files.Count - $pending.Count); a instalar: $($pending.Count)"
        $pending.Keys | Sort-Object | ForEach-Object { Write-Host "  $_" }
        if ($DryRun) { Write-Host 'Prévia concluída; projeto não alterado.'; return }
        if ($pending.Count -eq 0) { Write-Host 'Starter já instalado nesta revisão; nenhuma alteração.'; return }
        if ((Read-Host 'Instalar esses arquivos? [s/N]') -notmatch '^(s|sim)$') {
            Write-Host 'Instalação cancelada.'; return
        }
        Assert-SafeDestination $full | Out-Null
        $pending = Get-PendingFiles $full $files
        Install-StagedFiles $full $pending
        Write-Host "Instalação concluída: $($pending.Count) arquivos novos; commit $PackageCommit"
    }
    finally {
        $checkedTemp = [IO.Path]::GetFullPath($temp)
        if (-not $checkedTemp.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase) -or
            (Split-Path -Leaf $checkedTemp) -notmatch '^sixteensquad-[0-9a-f]{32}$') {
            throw 'Limpeza temporária recusada: caminho inesperado.'
        }
        $tempItem = Get-Item -LiteralPath $checkedTemp -Force -ErrorAction SilentlyContinue
        if ($null -ne $tempItem) {
            if ($tempItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Limpeza temporária recusada: link/junction.' }
            Remove-Item -LiteralPath $checkedTemp -Recurse -Force
        }
    }
}

if ($MyInvocation.InvocationName -ne '.') {
    Invoke-SixteenSquadInstall -Destination $ProjectPath -DryRun:$Preview
}
