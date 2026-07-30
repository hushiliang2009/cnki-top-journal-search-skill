from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


_MODULE_NAME = "cnki_search_env._environment_catalog_lookup"


def _load_environment_catalog_module() -> ModuleType:
    cached = sys.modules.get(_MODULE_NAME)
    if cached is not None:
        return cached
    source = Path(__file__).resolve().parents[1] / "catalog_lookup.py"
    spec = importlib.util.spec_from_file_location(_MODULE_NAME, source)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载环境期刊目录解析器：{source.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(_MODULE_NAME, None)
        raise
    return module


_catalog = _load_environment_catalog_module()
DEFAULT_CATALOG: Path = _catalog.DEFAULT_CATALOG
lookup_journals = _catalog.lookup_journals
journals_by_group = _catalog.journals_by_group
validate_catalog = _catalog.validate_catalog
