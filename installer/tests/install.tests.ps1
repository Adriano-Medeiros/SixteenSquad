$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
. (Join-Path $PSScriptRoot '..\install.ps1')
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression

$caseRoot = Join-Path $PSScriptRoot ('case-' + [guid]::NewGuid().ToString('N'))
[IO.Directory]::CreateDirectory($caseRoot) | Out-Null
$passed = 0
function Check([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw "FALHOU: $Message" }
    $script:passed++
}
function Expect-Error([scriptblock]$Action, [string]$Message) {
    try { & $Action; throw "Erro esperado ausente: $Message" }
    catch {
        if ($_.Exception.Message -like 'Erro esperado ausente:*') { throw }
        $script:passed++
    }
}
function New-FixtureZip([string]$ZipPath, [string]$ExtraName, [switch]$MissingOne) {
    $prefix = "SixteenSquad-$PackageCommit/starter/"
    $z = [IO.Compression.ZipFile]::Open($ZipPath, [IO.Compression.ZipArchiveMode]::Create)
    try {
        $names = New-Object 'System.Collections.Generic.List[string]'
        $names.Add('AGENTS.md')
        Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot '..\..\starter\.codex\agents') -Filter '*.toml' | ForEach-Object { $names.Add('.codex/agents/' + $_.Name) }
        Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot '..\..\starter\.agents\skills') -Directory | ForEach-Object { $names.Add('.agents/skills/' + $_.Name + '/SKILL.md') }
        'SPEC','PLAN','TASK' | ForEach-Object { $names.Add('templates/' + $_ + '.md') }
        if ($MissingOne) { $names.Remove('templates/TASK.md') | Out-Null }
        if ($ExtraName) { $names.Add($ExtraName) }
        foreach ($name in $names) {
            $entry = $z.CreateEntry($prefix + $name)
            $stream = New-Object IO.StreamWriter ($entry.Open(), [Text.Encoding]::UTF8)
            try { $stream.Write("fixture: $name") }
            finally { $stream.Dispose() }
        }
    }
    finally { $z.Dispose() }
}

try {
    $zip = Join-Path $caseRoot 'valid.zip'
    $stage = Join-Path $caseRoot 'stage'
    [IO.Directory]::CreateDirectory($stage) | Out-Null
    New-FixtureZip $zip ''
    $files = Read-StarterArchive $zip $stage $PackageCommit
    Check ($files.Count -eq 35) 'composição completa de 35 arquivos'
    Check ($files.ContainsKey('.codex/agents/ag15_documentation.toml')) 'AG-15 presente'

    $badZip = Join-Path $caseRoot 'invalid.zip'
    [IO.File]::WriteAllText($badZip, 'not a zip')
    Expect-Error { Read-StarterArchive $badZip (Join-Path $caseRoot 'badstage') $PackageCommit | Out-Null } 'ZIP inválido'
    $shortZip = Join-Path $caseRoot 'missing.zip'
    New-FixtureZip $shortZip '' -MissingOne
    Expect-Error { Read-StarterArchive $shortZip (Join-Path $caseRoot 'missingstage') $PackageCommit | Out-Null } 'pacote incompleto'
    $escapeZip = Join-Path $caseRoot 'escape.zip'
    New-FixtureZip $escapeZip '../outside.md'
    Expect-Error { Read-StarterArchive $escapeZip (Join-Path $caseRoot 'escapestage') $PackageCommit | Out-Null } 'ZIP com saída da raiz'
    $uncZip = Join-Path $caseRoot 'unc.zip'
    New-FixtureZip $uncZip '\\server\share\data'
    Expect-Error { Read-StarterArchive $uncZip (Join-Path $caseRoot 'uncstage') $PackageCommit | Out-Null } 'ZIP UNC sintético'
    Expect-Error { Assert-SafeDestination '\\invalid-server\share\project' | Out-Null } 'destino UNC sintético'

    $destination = Join-Path $caseRoot 'project'
    [IO.Directory]::CreateDirectory($destination) | Out-Null
    [IO.File]::WriteAllText((Join-Path $destination 'AGENTS.md'), 'original')
    Expect-Error { Get-PendingFiles $destination $files | Out-Null } 'conflito deve interromper'
    Check (([IO.File]::ReadAllText((Join-Path $destination 'AGENTS.md'))) -eq 'original') 'conflito preserva conteúdo'
    [IO.File]::Delete((Join-Path $destination 'AGENTS.md'))

    $rollbackDest = Join-Path $caseRoot 'parent\nested'
    $missing = $files['templates/TASK.md']
    [IO.File]::Delete($missing)
    Expect-Error { Install-StagedFiles $rollbackDest $files } 'falha parcial na cópia'
    Check (-not (Test-Path -LiteralPath $rollbackDest)) 'reversão remove diretório do projeto'
    Check (-not (Test-Path -LiteralPath (Join-Path $caseRoot 'parent'))) 'reversão remove ancestrais criados'

    # Pacote novo, para teste de prévia e instalação repetida.
    $stage = Join-Path $caseRoot 'stage2'
    [IO.Directory]::CreateDirectory($stage) | Out-Null
    $files = Read-StarterArchive $zip $stage $PackageCommit
    function Get-OfficialArchive([string]$Uri, [string]$OutputPath) { [IO.File]::Copy($script:zip, $OutputPath) }
    $previewDest = Join-Path $caseRoot 'preview-project'
    Invoke-SixteenSquadInstall -Destination $previewDest -DryRun | Out-Null
    Check (-not (Test-Path -LiteralPath $previewDest)) 'prévia não altera projeto'
    function Read-Host { 's' }
    Invoke-SixteenSquadInstall -Destination $previewDest | Out-Null
    Check (@(Get-ChildItem -LiteralPath $previewDest -File -Recurse -Force).Count -eq 35) 'instalação cria 35 arquivos'
    Invoke-SixteenSquadInstall -Destination $previewDest | Out-Null
    Check (@(Get-ChildItem -LiteralPath $previewDest -File -Recurse -Force).Count -eq 35) 'repetição não duplica arquivos'
    [IO.File]::WriteAllText((Join-Path $previewDest 'AGENTS.md'), 'customização preexistente')
    Expect-Error { Invoke-SixteenSquadInstall -Destination $previewDest | Out-Null } 'customização impede atualização'
    Check (([IO.File]::ReadAllText((Join-Path $previewDest 'AGENTS.md'))) -eq 'customização preexistente') 'conflito não sobrescreve'

    function Get-OfficialArchive([string]$Uri, [string]$OutputPath) { throw 'falha de download sintética' }
    $downloadDest = Join-Path $caseRoot 'download-failure'
    Expect-Error { Invoke-SixteenSquadInstall -Destination $downloadDest | Out-Null } 'download falha antes de modificar projeto'
    Check (-not (Test-Path -LiteralPath $downloadDest)) 'falha download não altera projeto'

    function Get-OfficialArchive([string]$Uri, [string]$OutputPath) { throw [UnauthorizedAccessException]::new('permissão negada sintética') }
    $permissionDest = Join-Path $caseRoot 'permission-failure'
    Expect-Error { Invoke-SixteenSquadInstall -Destination $permissionDest | Out-Null } 'permissão negada sintética'
    Check (-not (Test-Path -LiteralPath $permissionDest)) 'permissão negada não altera projeto'
    Write-Output "PASSOU: $passed verificações"
}
finally {
    $full = [IO.Path]::GetFullPath($caseRoot)
    if (-not $full.StartsWith([IO.Path]::GetFullPath($PSScriptRoot) + [IO.Path]::DirectorySeparatorChar,
                              [StringComparison]::OrdinalIgnoreCase)) { throw 'Limpeza recusada fora da pasta de testes.' }
    if (Test-Path -LiteralPath $full) { Remove-Item -LiteralPath $full -Recurse -Force }
}
