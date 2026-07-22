#!/bin/sh
set -eu

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

install_skill "$codex_home/skills/top-journal-search-lists"
install_skill "$claude_home/skills/top-journal-search-lists"

runtime_root="$codex_home/runtimes/cnki-search"
mkdir -p "$runtime_root"
python3 -m venv "$runtime_root/.venv"
runtime_python="$runtime_root/.venv/bin/python"
"$runtime_python" -m pip install 'mcp>=1,<2' 'playwright>=1.45,<2'
python_path="$codex_home/skills/top-journal-search-lists/scripts"

if command -v codex >/dev/null 2>&1; then
  codex mcp remove cnki-search >/dev/null 2>&1 || true
  codex mcp add cnki-search --env "PYTHONPATH=$python_path" --env PYTHONUTF8=1 --env PYTHONIOENCODING=utf-8 -- "$runtime_python" -m cnki_search.mcp_server
fi
claude_code_config="$HOME/.claude.json"
if [ "$(uname -s)" = "Darwin" ]; then
  claude_desktop_config="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
else
  claude_desktop_config="$HOME/.config/Claude/claude_desktop_config.json"
fi
for config in "$claude_code_config" "$claude_desktop_config"; do
  if [ -f "$config" ]; then
    cp "$config" "$config.backup-$timestamp"
    printf 'Backup: %s\n' "$config.backup-$timestamp"
  fi
  "$runtime_python" "$claude_home/skills/top-journal-search-lists/scripts/cnki_search/install_config.py" merge-claude --config "$config" --skill-root "$claude_home/skills/top-journal-search-lists" --python "$runtime_python"
done

printf '%s\n' 'cnki-search installation completed. Restart the clients before verification.'
