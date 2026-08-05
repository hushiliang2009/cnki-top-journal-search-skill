"""生成或校验环境期刊目录 v4.0 的确定性产物。"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from environment_catalog_v4 import OutputPaths, SourcePaths, generate_outputs


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parent
DEFAULT_REFERENCES = PROJECT_ROOT / "references"
DEFAULT_MCPB_REFERENCES = PROJECT_ROOT / "mcpb" / "src" / "references"
AUDIT_DIRECTORY = REPOSITORY_ROOT / "docs" / "audits"


def in_repository_layout() -> bool:
    """判断当前是仓库检出还是解压后的发布包。

    完整审计 JSONL 按发布约定只留在仓库里，Skill ZIP 不携带它。发布包里没有
    `docs/audits/` 也没有 `.git/`；只要其中之一存在就按仓库处理，这样在仓库里
    误删审计目录仍会照常报错，而不是被当成发布布局悄悄跳过。
    """
    return AUDIT_DIRECTORY.is_dir() or (REPOSITORY_ROOT / ".git").exists()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只校验，不写入文件")
    parser.add_argument(
        "--references",
        type=Path,
        default=DEFAULT_REFERENCES,
        help="Skill references 目录",
    )
    parser.add_argument(
        "--mcpb-references",
        type=Path,
        default=DEFAULT_MCPB_REFERENCES,
        help="MCPB references 镜像目录",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    references = arguments.references.resolve()
    repository = in_repository_layout()
    paths = OutputPaths(
        baseline=references / "环境科学与工程学科顶尖期刊目录_v4.0.md",
        sources=SourcePaths.from_references(references),
        skill_references=references,
        mcpb_references=arguments.mcpb_references.resolve(),
        audit_jsonl=(
            AUDIT_DIRECTORY / "environment_journal_match_audit_v4.0.jsonl"
            if repository
            else None
        ),
        audit_markdown=(
            AUDIT_DIRECTORY / "environment_journal_match_audit_v4.0.md"
            if repository
            else None
        ),
    )
    try:
        output_hashes = generate_outputs(paths, check=arguments.check)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    for name, digest in output_hashes.items():
        print(f"{name}: {digest}")
    if not repository:
        # 明说跳过了什么，否则局部校验会被读成完整校验。
        print("docs/audits: skipped (发布包布局，未携带完整审计输出)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
