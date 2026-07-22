from __future__ import annotations

import argparse
import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path


SKILL_FILES = ("SKILL.md", "README.md")
ALLOWLIST = {
    "agents": ("openai.yaml",),
    "installers": ("install.ps1", "install.sh"),
    "references": (
        "Academic_Journal_Master_Directory_20260715.md",
        "cnki-search-reference.md",
    ),
    "scripts": ("catalog_lookup.py", "build_release.py"),
    "scripts/cnki_search": ("*.py",),
    "mcpb": ("manifest.json", "pyproject.toml", "uv.lock"),
    "mcpb/src": ("catalog_lookup.py", "server.py"),
    "mcpb/src/cnki_search": ("*.py",),
    "mcpb/src/references": ("Academic_Journal_Master_Directory_20260715.md",),
}
FORBIDDEN_PARTS = {".pytest_cache", "__pycache__", ".venv", "outputs"}
FORBIDDEN_FILES = {"Local State", "details.py", "downloads.py", "exporters.py", "fields.py", "syntax.py", "cli.py"}


def _copy_allowlisted_tree(source: Path, target: Path) -> None:
    for filename in SKILL_FILES:
        _copy_file(source / filename, target / filename)
    for relative_dir, patterns in ALLOWLIST.items():
        source_dir = source / relative_dir
        for pattern in patterns:
            for path in sorted(source_dir.glob(pattern)):
                if path.is_file():
                    _copy_file(path, target / path.relative_to(source))


def _copy_file(source: Path, target: Path) -> None:
    if source.name in FORBIDDEN_FILES or FORBIDDEN_PARTS & set(source.parts):
        raise ValueError(f"不允许打包的文件：{source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _zip_tree(source: Path, output: Path, *, prefix: str = "") -> None:
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        files = sorted(
            (item for item in source.rglob("*") if item.is_file()),
            key=lambda item: item.relative_to(source).as_posix(),
        )
        for path in files:
            relative = path.relative_to(source)
            if FORBIDDEN_PARTS & set(relative.parts) or path.name in FORBIDDEN_FILES:
                raise ValueError(f"暂存目录包含不允许的文件：{relative}")
            name = f"{prefix}/{relative.as_posix()}" if prefix else relative.as_posix()
            archive.write(path, name)


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
        _copy_allowlisted_tree(skill_root, skill_stage)
        mcpb_stage = skill_stage / "mcpb"
        _zip_tree(skill_stage, skill_zip, prefix="top-journal-search-lists")
        _zip_tree(mcpb_stage, mcpb_zip)

    artifacts = [skill_zip, mcpb_zip]
    checksums.write_text(
        "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in artifacts),
        encoding="utf-8",
    )
    return [*artifacts, checksums]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    build(skill_root, args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
