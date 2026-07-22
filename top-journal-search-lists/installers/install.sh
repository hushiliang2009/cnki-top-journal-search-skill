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

skill_source=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
timestamp=$(date +%Y%m%d-%H%M%S)
codex_home=${CODEX_HOME:-"$HOME/.codex"}
claude_home=${CLAUDE_CONFIG_DIR:-"$HOME/.claude"}

install_skill() {
  destination=$1
  mkdir -p "$(dirname -- "$destination")"
  if [ -e "$destination" ]; then
    backup="$destination.backup-$timestamp"
    mv "$destination" "$backup"
    printf 'Backup: %s\n' "$backup"
  fi
  cp -R "$skill_source" "$destination"
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
if [ "$codex" = true ]; then
  codex_config="$codex_home/config.toml"
  if [ -f "$codex_config" ]; then
    cp "$codex_config" "$codex_config.backup-$timestamp"
    printf 'Backup: %s\n' "$codex_config.backup-$timestamp"
  fi
  "$runtime_python" "$codex_skill/scripts/cnki_search/install_config.py" merge-codex --config "$codex_config" --skill-root "$codex_skill" --python "$runtime_python"
fi
if [ "$claude_code" = true ]; then
  claude_code_config="$HOME/.claude.json"
  if [ -f "$claude_code_config" ]; then
    cp "$claude_code_config" "$claude_code_config.backup-$timestamp"
    printf 'Backup: %s\n' "$claude_code_config.backup-$timestamp"
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
  fi
  "$runtime_python" "$claude_skill/scripts/cnki_search/install_config.py" merge-claude --config "$claude_desktop_config" --skill-root "$claude_skill" --python "$runtime_python"
fi

printf '%s\n' 'cnki-search installation completed. Restart the clients before verification.'
