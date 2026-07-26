from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import tomllib


ROOT = Path(__file__).resolve().parents[1]
LAYOUTS = {
    "skill": ROOT / "scripts" / "cnki_search_env" / "install_config.py",
    "mcpb": ROOT / "mcpb" / "src" / "cnki_search_env" / "install_config.py",
}


def _load_layout(path: Path):
    module_name = f"install_config_security_{path.parent.parent.name}"
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
        Path(r"C:\研究资料\top-journal-search-lists-env"),
        Path(r"C:\运行时\python.exe"),
    )


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
def test_server_config_uses_environment_private_playwright_cache(layout: Path) -> None:
    module = _load_layout(layout)
    python_executable = Path(
        r"C:\研究资料\runtimes\cnki-search-env\.venv\Scripts\python.exe"
    )
    config = module.cnki_server_config(
        Path(r"C:\研究资料\top-journal-search-lists-env"),
        python_executable,
    )

    assert config["env"]["PLAYWRIGHT_BROWSERS_PATH"] == str(
        python_executable.parent.parent.parent / "playwright-browsers"
    )


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
def test_environment_server_coexists_with_generic_cnki_server(layout: Path) -> None:
    module = _load_layout(layout)
    existing = (
        "[mcp_servers.cnki-search]\n"
        'command = "generic-python"\n'
        'args = ["-m", "cnki_search.mcp_server"]\n'
    )

    merged = module.merge_codex_config(existing, _server_config(module))

    parsed = tomllib.loads(merged)
    assert parsed["mcp_servers"]["cnki-search"]["command"] == "generic-python"
    assert parsed["mcp_servers"]["cnki-search-env"] == _server_config(module)


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
def test_malformed_toml_is_rejected_before_write_with_readable_cli_error(
    layout: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_layout(layout)
    config = tmp_path / layout.parent.parent.name / "config.toml"
    config.parent.mkdir(parents=True)
    original = (
        b'[mcp_servers.cnki-search-env]\ncommand="old"\n[profiles.default\n'
        b'model="must-not-be-lost"\n'
    )
    config.write_bytes(original)

    result = module.main(
        [
            "merge-codex", "--config", str(config), "--skill-root", r"C:\研究资料\skill",
            "--python", r"C:\运行时\python.exe",
        ]
    )

    captured = capsys.readouterr()
    assert result != 0
    assert "配置合并失败" in captured.err
    assert "Traceback" not in captured.err
    assert config.read_bytes() == original
    assert not list(config.parent.glob(f".{config.name}.*.tmp"))


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
def test_merge_removes_all_cnki_child_tables_and_preserves_custom_values(layout: Path) -> None:
    module = _load_layout(layout)
    existing = r'''[mcp_servers.custom]
command = 'C:\工具\custom.exe'
token = "${CUSTOM_TOKEN}"

[[mcp_servers.custom.headers]]
name = "X-Api-Key"
value = "${CUSTOM_TOKEN}"

[mcp_servers.cnki-search-env]
command = "old"

[mcp_servers.cnki-search-env.env]
OLD = "must-be-removed"

[[mcp_servers.cnki-search-env.headers]]
name = "X-Old-Key"
value = "old-secret"
'''

    merged = module.merge_codex_config(existing, _server_config(module))

    assert "old-secret" not in merged and "must-be-removed" not in merged
    parsed = tomllib.loads(merged)
    assert parsed["mcp_servers"]["custom"] == {
        "command": r"C:\工具\custom.exe",
        "token": "${CUSTOM_TOKEN}",
        "headers": [{"name": "X-Api-Key", "value": "${CUSTOM_TOKEN}"}],
    }
    assert parsed["mcp_servers"]["cnki-search-env"] == _server_config(module)


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
def test_root_inline_mcp_servers_keeps_custom_values_and_adds_cnki(layout: Path) -> None:
    module = _load_layout(layout)
    existing = (
        'mcp_servers = { custom = { command = "custom-mcp", token = "${CUSTOM_TOKEN}", '
        "path = 'C:\\中文\\custom.exe' } }\n"
    )

    merged = module.merge_codex_config(existing, _server_config(module))

    parsed = tomllib.loads(merged)
    assert parsed["mcp_servers"]["custom"] == {
        "command": "custom-mcp",
        "token": "${CUSTOM_TOKEN}",
        "path": r"C:\中文\custom.exe",
    }
    assert parsed["mcp_servers"]["cnki-search-env"] == _server_config(module)


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
@pytest.mark.parametrize(
    "existing",
    (
        'mcp_servers.cnki-search-env.command = "old-python"\n',
        '[mcp_servers]\ncnki-search-env = { command = "old-python" }\n',
        'mcp_servers = { "cnki-search-env" = { command = "old-python" } }\n',
    ),
)
def test_unsafe_cnki_inline_or_dotted_definition_reports_actionable_error(
    layout: Path, existing: str,
) -> None:
    module = _load_layout(layout)

    with pytest.raises(ValueError, match=r"安全替换|table notation|手工删除"):
        module.merge_codex_config(existing, _server_config(module))


@pytest.mark.parametrize("layout", LAYOUTS.values(), ids=LAYOUTS)
def test_atomic_write_fsyncs_uses_unique_sibling_temp_and_cleans_on_replace_failure(
    layout: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_layout(layout)
    config = tmp_path / layout.parent.parent.name / "config.toml"
    config.parent.mkdir(parents=True)
    original = b'[mcp_servers.zotero]\ncommand = "zotero-mcp"\n'
    config.write_bytes(original)
    fsync_calls: list[int] = []
    temporary_calls: list[tuple[object, object, object]] = []
    real_mkstemp = module.tempfile.mkstemp

    def record_mkstemp(*, prefix: str, suffix: str, dir: Path):
        temporary_calls.append((prefix, suffix, dir))
        return real_mkstemp(prefix=prefix, suffix=suffix, dir=dir)

    def record_fsync(descriptor: int) -> None:
        fsync_calls.append(descriptor)

    def fail_replace(_source: Path, _target: Path) -> None:
        raise OSError("simulated replace failure")

    monkeypatch.setattr(module.tempfile, "mkstemp", record_mkstemp)
    monkeypatch.setattr(module.os, "fsync", record_fsync)
    monkeypatch.setattr(module.os, "replace", fail_replace)
    with pytest.raises(OSError, match="simulated replace failure"):
        module.main(
            [
                "merge-codex", "--config", str(config), "--skill-root", r"C:\研究资料\skill",
                "--python", r"C:\运行时\python.exe",
            ]
        )

    assert fsync_calls
    assert temporary_calls == [(f".{config.name}.", ".tmp", config.parent)]
    assert config.read_bytes() == original
    assert not list(config.parent.glob(f".{config.name}.*.tmp"))
