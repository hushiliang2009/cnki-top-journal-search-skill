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
    paths = OutputPaths(
        baseline=references / "环境科学与工程学科顶尖期刊目录_v4.0.md",
        sources=SourcePaths.from_references(references),
        skill_references=references,
        mcpb_references=arguments.mcpb_references.resolve(),
        audit_jsonl=(
            REPOSITORY_ROOT / "docs" / "audits" / "environment_journal_match_audit_v4.0.jsonl"
        ),
        audit_markdown=(
            REPOSITORY_ROOT / "docs" / "audits" / "environment_journal_match_audit_v4.0.md"
        ),
    )
    try:
        output_hashes = generate_outputs(paths, check=arguments.check)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    for name, digest in output_hashes.items():
        print(f"{name}: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
