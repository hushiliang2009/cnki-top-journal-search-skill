param(
    [switch]$Codex,
    [switch]$ClaudeCode,
    [switch]$ClaudeDesktop
)

$ErrorActionPreference = 'Stop'
if (-not ($Codex -or $ClaudeCode -or $ClaudeDesktop)) {
    Write-Error 'Usage: .\install.ps1 -Codex | -ClaudeCode | -ClaudeDesktop (one or more targets)'
    exit 2
}

$SkillSource = Join-Path (Split-Path -Parent $PSScriptRoot) 'top-journal-search-lists'
if (-not (Test-Path -LiteralPath $SkillSource -PathType Container)) {
    throw "未找到 Skill 源目录：$SkillSource"
}
$TimeStamp = Get-Date -Format 'yyyyMMdd-HHmmss'

function Backup-File([string]$Path) {
    if (Test-Path -LiteralPath $Path) {
        $Backup = "$Path.backup-$TimeStamp"
        Copy-Item -LiteralPath $Path -Destination $Backup
        Write-Host "Backup: $Backup"
    }
}

function Install-SkillCopy([string]$Destination) {
    $Parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    if (Test-Path -LiteralPath $Destination) {
        $Backup = "$Destination.backup-$TimeStamp"
        Move-Item -LiteralPath $Destination -Destination $Backup
        Write-Host "Backup: $Backup"
    }
    Copy-Item -LiteralPath $SkillSource -Destination $Destination -Recurse
}

$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$ClaudeHome = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $env:USERPROFILE '.claude' }

$CodexSkill = Join-Path $CodexHome 'skills\top-journal-search-lists'
$ClaudeSkill = Join-Path $ClaudeHome 'skills\top-journal-search-lists'
if ($Codex) { Install-SkillCopy $CodexSkill }
if ($ClaudeCode -or $ClaudeDesktop) { Install-SkillCopy $ClaudeSkill }

$RuntimeRoot = if ($Codex) { Join-Path $CodexHome 'runtimes\cnki-search' } else { Join-Path $ClaudeHome 'runtimes\cnki-search' }
New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null
$Python = (Get-Command python -ErrorAction Stop).Source
& $Python -m venv (Join-Path $RuntimeRoot '.venv')
$RuntimePython = Join-Path $RuntimeRoot '.venv\Scripts\python.exe'
& $RuntimePython -m pip install 'mcp>=1,<2' 'playwright>=1.45,<2'

if ($Codex -and (Get-Command codex -ErrorAction SilentlyContinue)) {
    Backup-File (Join-Path $CodexHome 'config.toml')
    & codex mcp remove cnki-search 2>$null
    & codex mcp add cnki-search --env "PYTHONPATH=$(Join-Path $CodexSkill 'scripts')" --env PYTHONUTF8=1 --env PYTHONIOENCODING=utf-8 -- $RuntimePython -m cnki_search.mcp_server
}
if ($ClaudeCode) {
    $ClaudeCodeConfig = Join-Path $env:USERPROFILE '.claude.json'
    Backup-File $ClaudeCodeConfig
    & $RuntimePython (Join-Path $ClaudeSkill 'scripts\cnki_search\install_config.py') merge-claude --config $ClaudeCodeConfig --skill-root $ClaudeSkill --python $RuntimePython
}
if ($ClaudeDesktop) {
    $ClaudeDesktopConfig = Join-Path $env:APPDATA 'Claude\claude_desktop_config.json'
    Backup-File $ClaudeDesktopConfig
    & $RuntimePython (Join-Path $ClaudeSkill 'scripts\cnki_search\install_config.py') merge-claude --config $ClaudeDesktopConfig --skill-root $ClaudeSkill --python $RuntimePython
}

Write-Host 'cnki-search installation completed. Restart the clients before verification.'
