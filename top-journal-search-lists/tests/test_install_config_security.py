from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import tomllib


ROOT = Path(__file__).resolve().parents[1]
LAYOUTS = {
    "skill": ROOT / "scripts" / "cnki_search" / "install_config.py",
    "mcpb": ROOT / "mcpb" / "src" / "cnki_search" / "install_config.py",
}


def _load_layout(path: Path):
    module_name = f"install_config_{path.parent.parent.name}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    return module


def _server_config(module):
    return module.cnki_server_config(
        Path(r"C:\研究资料\top-journal-search-lists"),
        Path(r"C:\运行时\python.exe"),
    )


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
def test_merge_removes_cnki_array_tables_and_preserves_custom_array_tables(layout: Path) -> None:
    module = _load_layout(layout)
    existing = """[[mcp_servers.custom.headers]]
name = "X-Api-Key"
value = "${CUSTOM_TOKEN}"

[[mcp_servers.cnki-search.headers]]
name = "X-Old-Key"
value = "old-secret"

[profiles.default]
model = "gpt-5"
"""

    merged = module.merge_codex_config(existing, _server_config(module))

    assert "X-Old-Key" not in merged
    assert "[[mcp_servers.custom.headers]]\nname = \"X-Api-Key\"\nvalue = \"${CUSTOM_TOKEN}\"" in merged
    parsed = tomllib.loads(merged)
    assert parsed["mcp_servers"]["custom"]["headers"] == [
        {"name": "X-Api-Key", "value": "${CUSTOM_TOKEN}"}
    ]
    assert parsed["profiles"]["default"] == {"model": "gpt-5"}
    assert parsed["mcp_servers"]["cnki-search"] == _server_config(module)


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
def test_merge_rejects_malformed_original_toml_before_removing_cnki_sections(layout: Path) -> None:
    module = _load_layout(layout)
    malformed = "[mcp_servers.cnki-search]\ncommand = [\n"

    with pytest.raises(tomllib.TOMLDecodeError):
        module.merge_codex_config(malformed, _server_config(module))


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
@pytest.mark.parametrize(
    "existing",
    (
        'mcp_servers.cnki-search.command = "old-python"\n',
        '[mcp_servers]\ncnki-search = { command = "old-python" }\n',
        'mcp_servers = { "cnki-search" = { command = "old-python" } }\n',
    ),
)
def test_merge_rejects_dotted_or_inline_cnki_definitions_with_guidance(
    layout: Path, existing: str,
) -> None:
    module = _load_layout(layout)

    with pytest.raises(ValueError, match=r"unsupported.*cnki-search"):
        module.merge_codex_config(existing, _server_config(module))


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
def test_merge_preserves_root_inline_mcp_servers_without_cnki(layout: Path) -> None:
    module = _load_layout(layout)
    existing = 'mcp_servers = { custom = { command = "custom-mcp", token = "${CUSTOM_TOKEN}" } }\n'

    merged = module.merge_codex_config(existing, _server_config(module))

    parsed = tomllib.loads(merged)
    assert parsed["mcp_servers"]["custom"] == {
        "command": "custom-mcp",
        "token": "${CUSTOM_TOKEN}",
    }
    assert parsed["mcp_servers"]["cnki-search"] == _server_config(module)


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
def test_claude_merge_replaces_only_cnki_server_with_nested_fields_and_chinese_paths(layout: Path) -> None:
    module = _load_layout(layout)
    existing = {
        "mcpServers": {
            "cnki-search": {"command": "old-python", "env": {"TOKEN": "old"}},
            "custom": {
                "command": r"C:\工具\custom.exe",
                "headers": [{"name": "Authorization", "value": "${CUSTOM_SECRET}"}],
            },
        },
        "preferences": {"nested": {"keep": ["中文路径", "${PLACEHOLDER}"]}},
    }

    merged = module.merge_claude_config(existing, _server_config(module))

    assert merged["mcpServers"]["cnki-search"] == _server_config(module)
    assert merged["mcpServers"]["custom"] == existing["mcpServers"]["custom"]
    assert merged["preferences"] == existing["preferences"]
    assert existing["mcpServers"]["cnki-search"]["command"] == "old-python"


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
def test_cli_preserves_original_and_cleans_unique_temp_file_when_replace_fails(
    layout: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_layout(layout)
    config = tmp_path / layout.parent.parent.name / "config.toml"
    config.parent.mkdir(parents=True)
    original = '[mcp_servers.zotero]\ncommand = "zotero-mcp"\n'
    config.write_text(original, encoding="utf-8")

    def fail_replace(_source: Path, _target: Path) -> None:
        raise OSError("simulated replace failure")

    monkeypatch.setattr(module.os, "replace", fail_replace)
    with pytest.raises(OSError, match="simulated replace failure"):
        module.main(
            [
                "merge-codex",
                "--config",
                str(config),
                "--skill-root",
                r"C:\研究资料\top-journal-search-lists",
                "--python",
                r"C:\运行时\python.exe",
            ]
        )

    assert config.read_text(encoding="utf-8") == original
    assert not list(config.parent.glob(f".{config.name}.*.tmp"))
    assert not (config.parent / f"{config.name}.tmp").exists()
