"""比对两个平台构建的发布产物，验证内容级可复现性。

整体 SHA-256 不可跨平台比较：deflate 的压缩字节流取决于 Python 链接的 zlib 实现
（例如 zlib-ng 与标准 zlib 对同一输入产生不同但同样合法的压缩流），因此同样的内容
在不同平台会得到不同的归档哈希。

真正应当跨平台恒定的是**解压后的内容**：成员集合、顺序、每个成员的 CRC 与字节，
以及打包元数据（固定时间戳与权限位）。本脚本只校验这些，不比较压缩后的大小或
归档哈希。

用法：
    python scripts/compare_release_content.py <目录A> <目录B>

两个目录各自包含 build_release.py 的输出。同名产物逐一比对，任一不一致即以非零退出。
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ARCHIVE_SUFFIXES = (".zip", ".mcpb")
METADATA_FIELDS = ("date_time", "external_attr", "create_system", "compress_type")


def _archives(directory: Path) -> dict[str, Path]:
    return {
        item.name: item
        for item in sorted(directory.iterdir())
        if item.is_file() and item.suffix in ARCHIVE_SUFFIXES
    }


def compare_archive(left: Path, right: Path) -> list[str]:
    problems: list[str] = []
    with zipfile.ZipFile(left) as a, zipfile.ZipFile(right) as b:
        names_a, names_b = a.namelist(), b.namelist()
        if names_a != names_b:
            only_a = sorted(set(names_a) - set(names_b))
            only_b = sorted(set(names_b) - set(names_a))
            if only_a:
                problems.append(f"{left.name}: 仅 A 有 {only_a[:5]}")
            if only_b:
                problems.append(f"{left.name}: 仅 B 有 {only_b[:5]}")
            if not only_a and not only_b:
                problems.append(f"{left.name}: 成员顺序不同")
            return problems

        info_a = {item.filename: item for item in a.infolist()}
        info_b = {item.filename: item for item in b.infolist()}
        for name in names_a:
            ia, ib = info_a[name], info_b[name]
            for field in METADATA_FIELDS:
                va, vb = getattr(ia, field), getattr(ib, field)
                if va != vb:
                    problems.append(f"{left.name}:{name} {field} 不同 A={va!r} B={vb!r}")
            if ia.CRC != ib.CRC:
                problems.append(f"{left.name}:{name} CRC 不同")
                continue
            if a.read(name) != b.read(name):
                problems.append(f"{left.name}:{name} 解压内容不同（CRC 相同，异常）")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    left_dir, right_dir = Path(argv[0]).resolve(), Path(argv[1]).resolve()
    left, right = _archives(left_dir), _archives(right_dir)

    if set(left) != set(right):
        print(f"产物文件名不一致：A={sorted(left)} B={sorted(right)}", file=sys.stderr)
        return 1
    if not left:
        print(f"未找到任何归档：{left_dir}", file=sys.stderr)
        return 1

    problems: list[str] = []
    for name in sorted(left):
        problems.extend(compare_archive(left[name], right[name]))

    for name in sorted(left):
        checks = (left_dir / "checksums.sha256", right_dir / "checksums.sha256")
        if all(path.is_file() for path in checks):
            a_names = {line.split("  ", 1)[1] for line in checks[0].read_text(encoding="utf-8").split("\n") if "  " in line}
            b_names = {line.split("  ", 1)[1] for line in checks[1].read_text(encoding="utf-8").split("\n") if "  " in line}
            if a_names != b_names:
                problems.append(f"checksums.sha256 列出的文件名不同：A={sorted(a_names)} B={sorted(b_names)}")
        break

    if problems:
        print("跨平台内容比对失败：", file=sys.stderr)
        for problem in problems[:40]:
            print(f"  {problem}", file=sys.stderr)
        print(f"共 {len(problems)} 处", file=sys.stderr)
        return 1

    print(f"跨平台内容一致：{len(left)} 个归档，成员、CRC、解压字节与打包元数据全部相同")
    print("（未比较归档 SHA-256：压缩流依赖 zlib 实现，跨平台本就不同）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
