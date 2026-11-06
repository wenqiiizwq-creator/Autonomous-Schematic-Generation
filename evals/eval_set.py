"""Where the circuit evaluation set lives. It is shared with the other skill and kept with the design rules, outside this
repository: `CIRCUIT_EVAL_SET`, else the default path. A checkout without it still runs the code gate; tests that need the set skip."""
import importlib.util
import json
import os
import sys
from pathlib import Path

DEFAULT = Path.home() / 'Documents/知识库/HardwareWiki/原理图设计规范/评测集'


def root():
    return Path(os.environ.get('CIRCUIT_EVAL_SET') or DEFAULT)


def available():
    return (root() / '工具' / 'evalset.py').is_file()


def tool():
    """显式外部依赖：缺 E 单独报告 skip，不冒充代码门通过。"""
    if not available():
        print(json.dumps({'status': 'skip', 'scope': 'external_evaluation',
                          'reason': f'电路评测集不在 {root()}；设 CIRCUIT_EVAL_SET 指向它'}, ensure_ascii=False))
        raise SystemExit(0)
    sys.path.insert(0, str(root() / '工具'))
    spec = importlib.util.spec_from_file_location('selected_evalset', root() / '工具/evalset.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def context(release, skill_root):
    return tool().binding.context(release, root(), skill_root)
