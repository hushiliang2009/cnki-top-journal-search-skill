param(
    [switch]$Codex,
    [switch]$ClaudeCode,
    [switch]$ClaudeDesktop,
    [string]$PythonExe = 'python',
    [string]$InternalRuntimePython,
    [string]$InternalTimeStamp,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArguments
)

$ErrorActionPreference = 'Stop'
if ($RemainingArguments.Count -gt 0 -or -not ($Codex -or $ClaudeCode -or $ClaudeDesktop)) {
    [Console]::Error.WriteLine('Usage: .\install.ps1 -Codex | -ClaudeCode | -ClaudeDesktop [-PythonExe path]')
    exit 2
}

function Assert-PythonVersion([string]$Command) {
    $versionOutput = (& $Command --version 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $versionOutput -notmatch 'Python\s+(\d+)\.(\d+)') {
        throw "Unable to determine Python version from '$Command': $versionOutput. Python 3.11 or higher is required."
    }
    $major = [int]$Matches[1]
    $minor = [int]$Matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
        throw "Detected $versionOutput from '$Command'. Python 3.11 or higher is required."
    }
}

function Assert-LastExit([string]$Description) {
    if ($LASTEXITCODE -ne 0) { throw "$Description failed, exit code: $LASTEXITCODE" }
}

$MovedSkills = @()
$CreatedSkills = @()
$BackedUpConfigs = @()
$CreatedConfigs = @()
$BackupTargets = @()

function Backup-Config([string]$Path) {
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        $backup = "$Path.backup-$TimeStamp"
        Copy-Item -LiteralPath $Path -Destination $backup -ErrorAction Stop
        $script:BackedUpConfigs += [pscustomobject]@{ Path = $Path; Backup = $backup }
        $script:BackupTargets += $Path
    }
    else {
        $script:CreatedConfigs += $Path
    }
}

function Install-SkillCopy([string]$Destination) {
    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    if (Test-Path -LiteralPath $Destination) {
        $backup = "$Destination.backup-$TimeStamp"
        Move-Item -LiteralPath $Destination -Destination $backup -ErrorAction Stop
        $script:MovedSkills += [pscustomobject]@{ Path = $Destination; Backup = $backup }
        $script:BackupTargets += $Destination
    }
    else {
        $script:CreatedSkills += $Destination
    }
    & $Python (Join-Path $SkillSource 'scripts\build_release.py') --copy-skill $Destination
    Assert-LastExit 'Copying the allowlisted Skill'
}

function Restore-Transaction {
    foreach ($path in $script:CreatedConfigs) {
        if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
    }
    foreach ($record in $script:BackedUpConfigs) {
        Copy-Item -LiteralPath $record.Backup -Destination $record.Path -Force
    }
    foreach ($path in $script:CreatedSkills) {
        if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Recurse -Force }
    }
    foreach ($record in $script:MovedSkills) {
        if (Test-Path -LiteralPath $record.Path) { Remove-Item -LiteralPath $record.Path -Recurse -Force }
        if (Test-Path -LiteralPath $record.Backup) {
            Move-Item -LiteralPath $record.Backup -Destination $record.Path -Force
        }
    }
}

function Rotate-Backups([string]$Path) {
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) { return }
    $leaf = Split-Path -Leaf $Path
    $pattern = '^' + [regex]::Escape($leaf) + '\.backup-\d{8}-\d{6}$'
    $backups = @(
        Get-ChildItem -LiteralPath $parent -Force |
            Where-Object { $_.Name -match $pattern } |
            Sort-Object Name -Descending
    )
    for ($index = 0; $index -lt $backups.Count; $index++) {
        $backup = $backups[$index]
        if ($index -lt 3) {
            Write-Host "Backup retained: $($backup.FullName)"
        }
        else {
            Remove-Item -LiteralPath $backup.FullName -Recurse -Force
            Write-Host "Backup removed: $($backup.FullName)"
        }
    }
}

$Python = $PythonExe
Assert-PythonVersion $Python

$SkillSource = Split-Path -Parent $PSScriptRoot
$TimeStamp = if ($InternalTimeStamp) { $InternalTimeStamp } else { Get-Date -Format 'yyyyMMdd-HHmmss' }
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$ClaudeHome = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $env:USERPROFILE '.claude' }
$Succeeded = $false

try {
    $CodexSkill = Join-Path $CodexHome 'skills\top-journal-search-lists'
    $ClaudeSkill = Join-Path $ClaudeHome 'skills\top-journal-search-lists'
    if ($Codex) { Install-SkillCopy $CodexSkill }
    if ($ClaudeCode -or $ClaudeDesktop) { Install-SkillCopy $ClaudeSkill }
    $InstalledSkill = if ($Codex) { $CodexSkill } else { $ClaudeSkill }

    $RuntimeRoot = if ($Codex) { Join-Path $CodexHome 'runtimes\cnki-search' } else { Join-Path $ClaudeHome 'runtimes\cnki-search' }
    New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null
    $RuntimePython = if ($InternalRuntimePython) { $InternalRuntimePython } else { Join-Path $RuntimeRoot '.venv\Scripts\python.exe' }
    if (-not (Test-Path -LiteralPath $RuntimePython -PathType Leaf)) {
        & $Python -m venv (Join-Path $RuntimeRoot '.venv')
        Assert-LastExit 'Creating the CNKI runtime'
    }
    & $RuntimePython -m pip install 'mcp>=1,<2' 'playwright>=1.45,<2'
    Assert-LastExit 'Installing CNKI runtime dependencies'
    & $RuntimePython -m playwright install chromium chromium-headless-shell
    Assert-LastExit 'Installing the Playwright Chromium runtime'
    & $RuntimePython -c 'import mcp, playwright'
    Assert-LastExit 'Checking mcp and playwright imports'
    & $RuntimePython -c 'import sys; sys.path.insert(0, sys.argv[1]); import cnki_search.mcp_server' (Join-Path $InstalledSkill 'scripts')
    Assert-LastExit 'Checking the installed cnki_search.mcp_server import'
    & $RuntimePython -c 'from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(); browser.close(); p.stop()'
    Assert-LastExit 'Launching the offline Chromium self-check'

    if ($Codex) {
        $CodexConfig = Join-Path $CodexHome 'config.toml'
        Backup-Config $CodexConfig
        & $RuntimePython (Join-Path $CodexSkill 'scripts\cnki_search\install_config.py') merge-codex --config $CodexConfig --skill-root $CodexSkill --python $RuntimePython
        Assert-LastExit 'Writing the Codex configuration'
    }
    if ($ClaudeCode) {
        $ClaudeCodeConfig = Join-Path $env:USERPROFILE '.claude.json'
        Backup-Config $ClaudeCodeConfig
        & $RuntimePython (Join-Path $ClaudeSkill 'scripts\cnki_search\install_config.py') merge-claude --config $ClaudeCodeConfig --skill-root $ClaudeSkill --python $RuntimePython
        Assert-LastExit 'Writing the Claude Code configuration'
    }
    if ($ClaudeDesktop) {
        $ClaudeDesktopConfig = Join-Path $env:APPDATA 'Claude\claude_desktop_config.json'
        Backup-Config $ClaudeDesktopConfig
        & $RuntimePython (Join-Path $ClaudeSkill 'scripts\cnki_search\install_config.py') merge-claude --config $ClaudeDesktopConfig --skill-root $ClaudeSkill --python $RuntimePython
        Assert-LastExit 'Writing the Claude Desktop configuration'
    }
    $Succeeded = $true
}
catch {
    Restore-Transaction
    throw
}

if ($Succeeded) {
    foreach ($target in ($BackupTargets | Select-Object -Unique)) { Rotate-Backups $target }
    Write-Host 'cnki-search installation completed. Restart the clients before verification.'
}
