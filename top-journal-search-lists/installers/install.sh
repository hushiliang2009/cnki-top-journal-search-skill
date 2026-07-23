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

python_command=${CNKI_PYTHON:-python3}

assert_python_version() {
  version_output=$("$python_command" --version 2>&1 || true)
  case "$version_output" in
    Python\ [0-9]*.[0-9]*) ;;
    *) printf '%s\n' "Unable to determine Python version from '$python_command': $version_output. Python 3.11 or higher is required." >&2; exit 1 ;;
  esac
  version=${version_output#Python }
  major=${version%%.*}
  remainder=${version#*.}
  minor=${remainder%%.*}
  if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 11 ]; }; then
    printf '%s\n' "Detected $version_output from '$python_command'. Python 3.11 or higher is required." >&2
    exit 1
  fi
}

assert_python_version

skill_source=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
timestamp=$(date +%Y%m%d-%H%M%S)
codex_home=${CODEX_HOME:-"$HOME/.codex"}
claude_home=${CLAUDE_CONFIG_DIR:-"$HOME/.claude"}
transaction_dir=$(mktemp -d "${TMPDIR:-/tmp}/cnki-install.XXXXXX")
install_complete=false

touch "$transaction_dir/moved_skills" "$transaction_dir/created_skills" \
  "$transaction_dir/backed_up_configs" "$transaction_dir/created_configs" "$transaction_dir/backup_targets"

rollback_transaction() {
  [ -d "$transaction_dir" ] || return
  while IFS='|' read -r path backup; do
    [ -n "$path" ] || continue
    [ -e "$path" ] && rm -f "$path"
    [ -f "$backup" ] && cp "$backup" "$path"
  done < "$transaction_dir/backed_up_configs"
  while IFS= read -r path; do
    [ -n "$path" ] && [ -e "$path" ] && rm -f "$path"
  done < "$transaction_dir/created_configs"
  while IFS= read -r path; do
    [ -n "$path" ] && [ -e "$path" ] && rm -rf "$path"
  done < "$transaction_dir/created_skills"
  while IFS='|' read -r path backup; do
    [ -n "$path" ] || continue
    [ -e "$path" ] && rm -rf "$path"
    [ -e "$backup" ] && mv "$backup" "$path"
  done < "$transaction_dir/moved_skills"
}

cleanup_transaction() {
  status=$?
  if [ "$install_complete" != true ]; then
    rollback_transaction
  fi
  rm -rf "$transaction_dir"
  trap - 0
  exit "$status"
}
trap cleanup_transaction 0

install_skill() {
  destination=$1
  mkdir -p "$(dirname -- "$destination")"
  if [ -e "$destination" ]; then
    backup="$destination.backup-$timestamp"
    mv "$destination" "$backup"
    printf '%s|%s\n' "$destination" "$backup" >> "$transaction_dir/moved_skills"
    printf '%s\n' "$destination" >> "$transaction_dir/backup_targets"
  else
    printf '%s\n' "$destination" >> "$transaction_dir/created_skills"
  fi
  "$python_command" "$skill_source/scripts/build_release.py" --copy-skill "$destination"
}

backup_config() {
  path=$1
  if [ -f "$path" ]; then
    backup="$path.backup-$timestamp"
    cp "$path" "$backup"
    printf '%s|%s\n' "$path" "$backup" >> "$transaction_dir/backed_up_configs"
    printf '%s\n' "$path" >> "$transaction_dir/backup_targets"
  else
    printf '%s\n' "$path" >> "$transaction_dir/created_configs"
  fi
}

rotate_backups() {
  path=$1
  parent=$(dirname -- "$path")
  leaf=$(basename -- "$path")
  [ -d "$parent" ] || return
  matching_backups=$(
    for backup in "$parent"/"$leaf".backup-????????-??????; do
      [ -e "$backup" ] || continue
      stamp=${backup##*.backup-}
      printf '%s' "$stamp" | grep -Eq '^[0-9]{8}-[0-9]{6}$' || continue
      printf '%s\n' "$backup"
    done | LC_ALL=C sort -r
  )
  index=0
  printf '%s\n' "$matching_backups" | while IFS= read -r backup; do
    [ -n "$backup" ] || continue
    if [ "$index" -lt 3 ]; then
      printf 'Backup retained: %s\n' "$backup"
    else
      rm -rf "$backup"
      printf 'Backup removed: %s\n' "$backup"
    fi
    index=$((index + 1))
  done
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
  installed_skill="$codex_skill"
else
  installed_skill="$claude_skill"
fi

if [ "$codex" = true ]; then
  runtime_root="$codex_home/runtimes/cnki-search"
else
  runtime_root="$claude_home/runtimes/cnki-search"
fi
mkdir -p "$runtime_root"
runtime_python="$runtime_root/.venv/bin/python"
if [ ! -x "$runtime_python" ]; then
  "$python_command" -m venv "$runtime_root/.venv"
fi
"$runtime_python" -m pip install 'mcp>=1,<2' 'playwright>=1.45,<2'
"$runtime_python" -m playwright install chromium chromium-headless-shell
"$runtime_python" -c 'import mcp, playwright'
"$runtime_python" -c 'import sys; sys.path.insert(0, sys.argv[1]); import cnki_search.mcp_server' "$installed_skill/scripts"
"$runtime_python" -c 'from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(); browser.close(); p.stop()'

if [ "$codex" = true ]; then
  codex_config="$codex_home/config.toml"
  backup_config "$codex_config"
  "$runtime_python" "$codex_skill/scripts/cnki_search/install_config.py" merge-codex --config "$codex_config" --skill-root "$codex_skill" --python "$runtime_python"
fi
if [ "$claude_code" = true ]; then
  claude_code_config="$HOME/.claude.json"
  backup_config "$claude_code_config"
  "$runtime_python" "$claude_skill/scripts/cnki_search/install_config.py" merge-claude --config "$claude_code_config" --skill-root "$claude_skill" --python "$runtime_python"
fi
if [ "$(uname -s)" = "Darwin" ]; then
  claude_desktop_config="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
else
  claude_desktop_config="$HOME/.config/Claude/claude_desktop_config.json"
fi
if [ "$claude_desktop" = true ]; then
  backup_config "$claude_desktop_config"
  "$runtime_python" "$claude_skill/scripts/cnki_search/install_config.py" merge-claude --config "$claude_desktop_config" --skill-root "$claude_skill" --python "$runtime_python"
fi

install_complete=true
while IFS= read -r target; do
  [ -n "$target" ] && rotate_backups "$target"
done < "$transaction_dir/backup_targets"
printf '%s\n' 'cnki-search installation completed. Restart the clients before verification.'
