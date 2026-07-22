param(
    [switch]$Codex,
    [switch]$ClaudeCode,
    [switch]$ClaudeDesktop,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArguments
)

$ErrorActionPreference = 'Stop'
if ($RemainingArguments.Count -gt 0 -or -not ($Codex -or $ClaudeCode -or $ClaudeDesktop)) {
    [Console]::Error.WriteLine('Usage: .\install.ps1 -Codex | -ClaudeCode | -ClaudeDesktop (one or more targets)')
    exit 2
}

$SkillSource = Split-Path -Parent $PSScriptRoot
$TimeStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Python = (Get-Command python -ErrorAction Stop).Source

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
    & $Python (Join-Path $SkillSource 'scripts\build_release.py') --copy-skill $Destination
    if ($LASTEXITCODE -ne 0) { throw "复制 Skill 白名单文件失败，退出码：$LASTEXITCODE" }
}

$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$ClaudeHome = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $env:USERPROFILE '.claude' }

$CodexSkill = Join-Path $CodexHome 'skills\top-journal-search-lists'
$ClaudeSkill = Join-Path $ClaudeHome 'skills\top-journal-search-lists'
if ($Codex) { Install-SkillCopy $CodexSkill }
if ($ClaudeCode -or $ClaudeDesktop) { Install-SkillCopy $ClaudeSkill }

$RuntimeRoot = if ($Codex) { Join-Path $CodexHome 'runtimes\cnki-search' } else { Join-Path $ClaudeHome 'runtimes\cnki-search' }
New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null
$RuntimePython = Join-Path $RuntimeRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $RuntimePython -PathType Leaf)) {
    & $Python -m venv (Join-Path $RuntimeRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw "创建 CNKI 运行时失败，退出码：$LASTEXITCODE" }
}
& $RuntimePython -m pip install 'mcp>=1,<2' 'playwright>=1.45,<2'
if ($LASTEXITCODE -ne 0) { throw "安装 CNKI 运行时依赖失败，退出码：$LASTEXITCODE" }

if ($Codex) {
    $CodexConfig = Join-Path $CodexHome 'config.toml'
    Backup-File $CodexConfig
    & $RuntimePython (Join-Path $CodexSkill 'scripts\cnki_search\install_config.py') merge-codex --config $CodexConfig --skill-root $CodexSkill --python $RuntimePython
    if ($LASTEXITCODE -ne 0) { throw "写入 Codex 配置失败，退出码：$LASTEXITCODE" }
}
if ($ClaudeCode) {
    $ClaudeCodeConfig = Join-Path $env:USERPROFILE '.claude.json'
    Backup-File $ClaudeCodeConfig
    & $RuntimePython (Join-Path $ClaudeSkill 'scripts\cnki_search\install_config.py') merge-claude --config $ClaudeCodeConfig --skill-root $ClaudeSkill --python $RuntimePython
    if ($LASTEXITCODE -ne 0) { throw "写入 Claude Code 配置失败，退出码：$LASTEXITCODE" }
}
if ($ClaudeDesktop) {
    $ClaudeDesktopConfig = Join-Path $env:APPDATA 'Claude\claude_desktop_config.json'
    Backup-File $ClaudeDesktopConfig
    & $RuntimePython (Join-Path $ClaudeSkill 'scripts\cnki_search\install_config.py') merge-claude --config $ClaudeDesktopConfig --skill-root $ClaudeSkill --python $RuntimePython
    if ($LASTEXITCODE -ne 0) { throw "写入 Claude Desktop 配置失败，退出码：$LASTEXITCODE" }
}

Write-Host 'cnki-search installation completed. Restart the clients before verification.'
