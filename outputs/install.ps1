param(
    [switch]$SkipClaude,
    [switch]$SkipCodex
)

$ErrorActionPreference = 'Stop'
$SkillSource = Split-Path -Parent $PSScriptRoot
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

if (-not $SkipCodex) { Install-SkillCopy (Join-Path $CodexHome 'skills\top-journal-search-lists') }
if (-not $SkipClaude) { Install-SkillCopy (Join-Path $ClaudeHome 'skills\top-journal-search-lists') }

$RuntimeRoot = Join-Path $CodexHome 'runtimes\cnki-search'
New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null
$Python = (Get-Command python -ErrorAction Stop).Source
& $Python -m venv (Join-Path $RuntimeRoot '.venv')
$RuntimePython = Join-Path $RuntimeRoot '.venv\Scripts\python.exe'
& $RuntimePython -m pip install 'mcp>=1,<2' 'playwright>=1.45,<2'

$InstalledSkill = if (-not $SkipCodex) { Join-Path $CodexHome 'skills\top-journal-search-lists' } else { Join-Path $ClaudeHome 'skills\top-journal-search-lists' }
$PythonPath = Join-Path $InstalledSkill 'scripts'
if (-not $SkipCodex -and (Get-Command codex -ErrorAction SilentlyContinue)) {
    Backup-File (Join-Path $CodexHome 'config.toml')
    & codex mcp remove cnki-search 2>$null
    & codex mcp add cnki-search --env "PYTHONPATH=$PythonPath" --env PYTHONUTF8=1 --env PYTHONIOENCODING=utf-8 -- $RuntimePython -m cnki_search.mcp_server
}
if (-not $SkipClaude) {
    $ClaudeCodeConfig = Join-Path $env:USERPROFILE '.claude.json'
    $ClaudeDesktopConfig = Join-Path $env:APPDATA 'Claude\claude_desktop_config.json'
    Backup-File $ClaudeCodeConfig
    Backup-File $ClaudeDesktopConfig
    & $RuntimePython (Join-Path $InstalledSkill 'scripts\cnki_search\install_config.py') merge-claude --config $ClaudeCodeConfig --skill-root $InstalledSkill --python $RuntimePython
    & $RuntimePython (Join-Path $InstalledSkill 'scripts\cnki_search\install_config.py') merge-claude --config $ClaudeDesktopConfig --skill-root $InstalledSkill --python $RuntimePython
}

Write-Host 'cnki-search installation completed. Restart the clients before verification.'
