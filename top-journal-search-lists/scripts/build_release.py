from __future__ import annotations

import argparse
import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path


CNKI_MODULES = (
    "__init__.py",
    "browser.py",
    "cache.py",
    "install_config.py",
    "mcp_server.py",
    "merge.py",
    "models.py",
    "ranking.py",
    "rate_limit.py",
    "results.py",
    "search.py",
    "service.py",
    "session.py",
)
TEST_ALLOWLIST = (
    "tests/conftest.py",
    "tests/test_catalog_lookup.py",
    "tests/test_cnki_cache.py",
    "tests/test_cnki_mcp.py",
    "tests/test_cnki_merge.py",
    "tests/test_cnki_models.py",
    "tests/test_cnki_package_contract.py",
    "tests/test_cnki_ranking.py",
    "tests/test_cnki_rate_limit.py",
    "tests/test_cnki_results.py",
    "tests/test_cnki_search.py",
    "tests/test_cnki_service.py",
    "tests/test_cnki_session.py",
    "tests/test_installers.py",
    "tests/test_mcpb_manifest.py",
    "tests/fixtures/public_challenge.html",
    "tests/fixtures/public_home.html",
    "tests/fixtures/public_incomplete_results.html",
    "tests/fixtures/public_no_results.html",
    "tests/fixtures/public_results.html",
    "tests/fixtures/public_results_nested_table.html",
    "tests/fixtures/public_results_with_paper_titles.html",
)
MCPB_ALLOWLIST = (
    "manifest.json",
    "pyproject.toml",
    "src/catalog_lookup.py",
    *(f"src/cnki_search/{name}" for name in CNKI_MODULES),
    "src/references/Academic_Journal_Master_Directory_20260715.md",
    "src/server.py",
    "uv.lock",
)
SKILL_ALLOWLIST = (
    "README.md",
    "SKILL.md",
    "agents/openai.yaml",
    "installers/install.ps1",
    "installers/install.sh",
    *(f"mcpb/{relative}" for relative in MCPB_ALLOWLIST),
    "references/Academic_Journal_Master_Directory_20260715.md",
    "references/cnki-search-reference.md",
    "scripts/build_release.py",
    "scripts/catalog_lookup.py",
    *(f"scripts/cnki_search/{name}" for name in CNKI_MODULES),
    *TEST_ALLOWLIST,
)
ALLOWLIST = SKILL_ALLOWLIST
ZIP_DATE_TIME = (1980, 1, 1, 0, 0, 0)
REGULAR_MODE = 0o100644
EXECUTABLE_MODE = 0o100755


def copy_skill_tree(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=False)
    for relative in SKILL_ALLOWLIST:
        source_file = source / relative
        if not source_file.is_file():
            raise FileNotFoundError(f"白名单文件不存在：{source_file}")
        target_file = target / relative
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_file, target_file)


def _zip_tree(source: Path, output: Path, *, prefix: str = "") -> None:
    files = sorted(
        (path for path in source.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(source).as_posix(),
    )
    with zipfile.ZipFile(
        output,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in files:
            relative = path.relative_to(source).as_posix()
            name = f"{prefix}/{relative}" if prefix else relative
            info = zipfile.ZipInfo(name, date_time=ZIP_DATE_TIME)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = EXECUTABLE_MODE if path.suffix == ".sh" else REGULAR_MODE
            info.external_attr = mode << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)


def build(skill_root: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_zip = output_dir / "top-journal-search-lists_Skill.zip"
    mcpb_zip = output_dir / "cnki-search.mcpb"
    checksums = output_dir / "checksums.sha256"
    for target in (skill_zip, mcpb_zip, checksums):
        target.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix="cnki-public-build-") as temporary:
        staging = Path(temporary)
        skill_stage = staging / "top-journal-search-lists"
        copy_skill_tree(skill_root, skill_stage)
        _zip_tree(skill_stage, skill_zip, prefix="top-journal-search-lists")
        _zip_tree(skill_stage / "mcpb", mcpb_zip)

    artifacts = [skill_zip, mcpb_zip]
    checksums.write_text(
        "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in artifacts),
        encoding="utf-8",
    )
    return [*artifacts, checksums]


def main() -> int:
    parser = argparse.ArgumentParser()
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--output", type=Path)
    target.add_argument("--copy-skill", type=Path)
    args = parser.parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    if args.copy_skill is not None:
        copy_skill_tree(skill_root, args.copy_skill.resolve())
    else:
        build(skill_root, args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
