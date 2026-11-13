"""单个测试需要知识框架时用：没配框架就跳过该测试并说明原因（整个模块都要框架的用 framework_required）。"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import knowledge_source


def _problem():
    try:
        knowledge_source.framework_root()
    except knowledge_source.KnowledgeFrameworkNotFound as exc:
        return '没有配置知识框架：%s' % str(exc).splitlines()[0]
    return None


def skip_without_framework(test):
    return unittest.skipIf(_problem() is not None, _problem() or '')(test)
