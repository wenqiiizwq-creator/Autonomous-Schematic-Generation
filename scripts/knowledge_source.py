#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""知识框架的定位：技能运行时直接读本机的“硬件设计知识框架”目录，所有脚本只从本模块取框架里的路径。

框架目录按下面两种办法之一指定（先环境变量，后本机文件），代码里不写任何默认的本机路径：
  1. 环境变量 HARDWARE_KNOWLEDGE_FRAMEWORK，值为框架目录的绝对路径；
  2. 技能根目录下的本机文件 .knowledge-framework（一行，写框架目录的绝对路径；已加进 .gitignore）。
取到的目录下必须有 知识/ 和 索引/，否则抛 KnowledgeFrameworkNotFound。

路径一律用函数取，import 时不解析，没配框架时 --help 之类的命令照样能跑。只用标准库。

    python3 knowledge_source.py        打印框架目录、读取日期和指纹
"""
import datetime
import hashlib
import json
import os
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
ENV_VAR = 'HARDWARE_KNOWLEDGE_FRAMEWORK'
LOCAL_FILE_NAME = '.knowledge-framework'
# 技能使用的七个知识组件（框架 知识/ 下的目录名）；设计实例、设计准则不在其内，准则由 guideline_criteria 读。
COMPONENTS = ('需求要素', '板级架构模式', '接口约定', '典型电路', '计算方法', '器件参数', '失效与故障分析')
INDEX_FILES = ('索引/条目总表.md', '索引/准则支撑表.md')
SINGLE_FILES = INDEX_FILES + ('原件勘误.md', '条目规范.md')
G10_DIR = '规范正文/G10_元器件降额与应力规范'


class KnowledgeFrameworkNotFound(ValueError):
    """找不到知识框架目录。"""


def _setup_hint():
    return ('请用下面任一办法指定硬件设计知识框架目录（该目录下要有 知识/ 和 索引/）：'
            '\n  1. 设环境变量 %s=<框架目录的绝对路径>；'
            '\n  2. 在技能根目录 %s 下建文件 %s，一行，写框架目录的绝对路径。'
            % (ENV_VAR, SKILL_ROOT, LOCAL_FILE_NAME))


def _check(path, origin):
    root = Path(path).expanduser()
    missing = [name for name in ('知识', '索引') if not (root / name).is_dir()]
    if missing:
        raise KnowledgeFrameworkNotFound('%s 指向的目录 %s 不是知识框架（缺少 %s/）。%s'
                                         % (origin, root, '、'.join(missing), _setup_hint()))
    return root


def framework_root():
    """知识框架目录：环境变量 HARDWARE_KNOWLEDGE_FRAMEWORK，其次技能根目录的 .knowledge-framework；每次调用重新取。"""
    value = os.environ.get(ENV_VAR, '').strip()
    if value:
        return _check(value, '环境变量 ' + ENV_VAR)
    local = SKILL_ROOT / LOCAL_FILE_NAME
    if local.is_file():
        lines = [line.strip() for line in local.read_text(encoding='utf-8').splitlines() if line.strip()]
        if lines:
            return _check(lines[0], '文件 ' + str(local))
    raise KnowledgeFrameworkNotFound('没有配置知识框架目录。' + _setup_hint())


def knowledge_dir():
    return framework_root() / '知识'


def index_dir():
    return framework_root() / '索引'


def guideline_dir():
    return knowledge_dir() / '设计准则'


def registry_dir():
    return guideline_dir() / '准则登记'


def vocabulary_path():
    return registry_dir() / '词表.json'


def _g10(name):
    return guideline_dir() / G10_DIR / name


def derating_path():
    return _g10('降额值.json')


def commodity_path():
    return _g10('常规件最弱档.json')


def derating_doc_path():
    return _g10('降额规范.md')


def stress_spec_path():
    return _g10('应力判法.md')


def errata_path():
    return framework_root() / '原件勘误.md'


def entry_spec_path():
    return framework_root() / '条目规范.md'


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def knowledge_files():
    """{相对框架目录的路径: sha256}：七个组件下的全部 .md、索引/ 的两个文件、原件勘误.md、条目规范.md。"""
    root = framework_root()
    missing = [name for name in COMPONENTS if not (root / '知识' / name).is_dir()] + \
              [name for name in SINGLE_FILES if not (root / name).is_file()]
    if missing:
        raise KnowledgeFrameworkNotFound('知识框架 %s 里没有：%s' % (root, '、'.join(missing)))
    files = {p.relative_to(root).as_posix(): _sha(p)
             for name in COMPONENTS for p in sorted((root / '知识' / name).rglob('*.md'))}
    files.update({name: _sha(root / name) for name in SINGLE_FILES})
    return files


def fingerprint(files):
    return hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def identity():
    """交付物里记的知识身份：读取日期和读到的知识文件的指纹（框架不维护版本号）。"""
    return {'read_date': datetime.date.today().isoformat(), 'fingerprint': fingerprint(knowledge_files())}


def label(ident=None):
    """交付物里写的一句话：知识框架 <指纹前 12 位>（<读取日期> 读取）。"""
    ident = identity() if ident is None else ident
    return '知识框架 %s（%s 读取）' % (ident['fingerprint'][:12], ident['read_date'])


def main():
    try:
        root = framework_root()
        ident = identity()
    except KnowledgeFrameworkNotFound as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print('%s\n%s' % (root, label(ident)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
