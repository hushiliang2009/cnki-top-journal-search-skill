#!/bin/sh
set -eu

usage() {
  printf '%s\n' 'Usage: ./install.sh --codex | --claude-code | --claude-desktop [additional targets]' >&2
}

codex=false
claude_code=false
claude_desktop=false
if [ "$#" -eq 0 ]; then
  usage
  exit 2
fi
while [ "$#" -gt 0 ]; do
  case "$1" in
    --codex) codex=true ;;
    --claude-code) claude_code=true ;;
    --claude-desktop) claude_desktop=true ;;
    *) usage; exit 2 ;;
  esac
  shift
done

# 版本闸必须在任何写操作之前：mcp 与 playwright 都支持 3.10，pip 会安装成功，
# 但 cnki_search 依赖 3.11+ 的 enum.StrEnum，服务器首次启动即崩溃且错误与安装
# 过程毫无关联。安装器不安装项目本身，pyproject.toml 的 requires-python 从不被
# pip 执行，因此必须在这里显式拦截；放在复制 Skill 之后会留下半装状态。
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
  printf '%s\n' "错误：cnki-search 需要 Python 3.11 或更高版本，当前为 $(python3 -V 2>&1)。请升级 Python 后重试。" >&2
  exit 1
fi

skill_source=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
timestamp=$(date +%Y%m%d-%H%M%S)
codex_home=${CODEX_HOME:-"$HOME/.codex"}
claude_home=${CLAUDE_CONFIG_DIR:-"$HOME/.claude"}

# 备份保留份数：此前无限累积，生产环境实测已积到 14 份、617.8 KB
BACKUP_KEEP=5

prune_backups() {
  # shellcheck disable=SC2012
  ls -1dt "$1".backup-* 2>/dev/null | tail -n "+$((BACKUP_KEEP + 1))" | while read -r stale; do
    rm -rf -- "$stale"
    printf 'Pruned old backup: %s\n' "$stale"
  done
}

install_skill() {
  destination=$1
  mkdir -p "$(dirname -- "$destination")"
  if [ -e "$destination" ]; then
    backup="$destination.backup-$timestamp"
    mv "$destination" "$backup"
    printf 'Backup: %s\n' "$backup"
    prune_backups "$destination"
  fi
  python3 "$skill_source/scripts/build_release.py" --copy-skill "$destination"
}

codex_skill="$codex_home/skills/top-journal-search-lists"
claude_skill="$claude_home/skills/top-journal-search-lists"
if [ "$codex" = true ]; then
  install_skill "$codex_skill"
fi
if [ "$claude_code" = true ] || [ "$claude_desktop" = true ]; then
  install_skill "$claude_skill"
fi

if [ "$codex" = true ]; then
  runtime_root="$codex_home/runtimes/cnki-search"
else
  runtime_root="$claude_home/runtimes/cnki-search"
fi
mkdir -p "$runtime_root"
runtime_python="$runtime_root/.venv/bin/python"
if [ ! -x "$runtime_python" ]; then
  python3 -m venv "$runtime_root/.venv"
fi
"$runtime_python" -m pip install 'mcp>=1,<2' 'playwright>=1.45,<2'
# 仅 install chromium 不会一并落地 headless shell，headless=True 启动会失败
"$runtime_python" -m playwright install chromium chromium-headless-shell
if [ "$codex" = true ]; then
  codex_config="$codex_home/config.toml"
  if [ -f "$codex_config" ]; then
    cp "$codex_config" "$codex_config.backup-$timestamp"
    printf 'Backup: %s\n' "$codex_config.backup-$timestamp"
    prune_backups "$codex_config"
  fi
  "$runtime_python" "$codex_skill/scripts/cnki_search/install_config.py" merge-codex --config "$codex_config" --skill-root "$codex_skill" --python "$runtime_python"
fi
if [ "$claude_code" = true ]; then
  claude_code_config="$HOME/.claude.json"
  if [ -f "$claude_code_config" ]; then
    cp "$claude_code_config" "$claude_code_config.backup-$timestamp"
    printf 'Backup: %s\n' "$claude_code_config.backup-$timestamp"
    prune_backups "$claude_code_config"
  fi
  "$runtime_python" "$claude_skill/scripts/cnki_search/install_config.py" merge-claude --config "$claude_code_config" --skill-root "$claude_skill" --python "$runtime_python"
fi
if [ "$(uname -s)" = "Darwin" ]; then
  claude_desktop_config="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
else
  claude_desktop_config="$HOME/.config/Claude/claude_desktop_config.json"
fi
if [ "$claude_desktop" = true ]; then
  if [ -f "$claude_desktop_config" ]; then
    cp "$claude_desktop_config" "$claude_desktop_config.backup-$timestamp"
    printf 'Backup: %s\n' "$claude_desktop_config.backup-$timestamp"
    prune_backups "$claude_desktop_config"
  fi
  "$runtime_python" "$claude_skill/scripts/cnki_search/install_config.py" merge-claude --config "$claude_desktop_config" --skill-root "$claude_skill" --python "$runtime_python"
fi

printf '%s\n' 'cnki-search installation completed. Restart the clients before verification.'
