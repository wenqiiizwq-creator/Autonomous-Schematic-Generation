"""没配知识框架时，import 本模块的测试文件整个跳过（框架位置的配法见 references/knowledge-package.md）。"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import knowledge_source

try:
    knowledge_source.framework_root()
except knowledge_source.KnowledgeFrameworkNotFound as exc:
    raise unittest.SkipTest('没有配置知识框架：%s' % str(exc).splitlines()[0])
