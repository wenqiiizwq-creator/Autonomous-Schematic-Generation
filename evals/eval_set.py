"""Where the circuit evaluation set lives. It is shared with the other skill and kept with the design rules, outside this
repository: `CIRCUIT_EVAL_SET`, else the default path. A checkout without it still runs the code gate; tests that need the set skip."""
import os
from pathlib import Path

DEFAULT = Path.home() / 'Documents/知识库/HardwareWiki/原理图设计规范/评测集'


def root():
    return Path(os.environ.get('CIRCUIT_EVAL_SET') or DEFAULT)


def available():
    return (root() / '工具' / 'evalset.py').is_file()
