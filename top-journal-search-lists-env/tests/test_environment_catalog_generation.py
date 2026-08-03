from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"
SCRIPT = ROOT / "scripts" / "environment_catalog_v4.py"


def _load_catalog_module():
    assert SCRIPT.is_file(), "环境 v4.0 来源解析器尚未实现"
    spec = importlib.util.spec_from_file_location("environment_catalog_v4", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_source_parsers_preserve_approved_counts_and_original_titles() -> None:
    """删除解析或按逗号拆分北大核心原刊名时，此测试应失败。"""
    catalog = _load_catalog_module()
    paths = catalog.SourcePaths.from_references(REFERENCES)
    ssci = catalog.parse_wos_csv(
        paths.ssci_csv,
        "SSCI",
        display_titles=catalog.parse_wos_markdown(paths.ssci_markdown),
    )
    scie = catalog.parse_wos_csv(
        paths.scie_csv,
        "SCIE",
        display_titles=catalog.parse_wos_markdown(paths.scie_markdown),
    )
    cssci = catalog.parse_cssci_markdown(paths.cssci_markdown)
    natural = catalog.parse_pku_markdown(paths.pku_natural, "natural_sciences")
    non_natural = catalog.parse_pku_markdown(
        paths.pku_non_natural, "non_natural_sciences"
    )

    assert [len(items) for items in (ssci, scie, cssci, natural, non_natural)] == [
        3538,
        9430,
        674,
        1247,
        740,
    ]
    renamed = next(item for item in natural if item.formal_title == "低碳化学与化工")
    assert renamed.aliases == ("天然气化工.C1,化学与化工",)
