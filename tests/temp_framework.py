"""测试用的临时知识框架：内容链接到本机配置的框架，只有 原件 换成给定目录（或没有），用 HARDWARE_KNOWLEDGE_FRAMEWORK 指过去。"""
import atexit
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import knowledge_source

_NO_RAW = []


def mirror(dest, raw=None):
    """dest 下建一个框架：配置的框架里除 原件 以外的各项都链接过来；raw 给了就把 原件 链接到它，没给就不建 原件（没有原件总库）。"""
    real = knowledge_source.framework_root()
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for item in real.iterdir():
        if item.name != knowledge_source.RAW_LINK and not item.name.startswith('.'):
            (dest / item.name).symlink_to(item)
    if raw is not None:
        (dest / knowledge_source.RAW_LINK).symlink_to(Path(raw).resolve())
    return dest


def minimal(dest, raw):
    """dest 下建一个只有 知识/、索引/ 和 原件（链接到 raw）的小框架：只用到原件总库的测试用，不需要本机配了框架。"""
    dest = Path(dest)
    for name in ('知识', '索引'):
        (dest / name).mkdir(parents=True, exist_ok=True)
    (dest / knowledge_source.RAW_LINK).symlink_to(Path(raw).resolve())
    return dest


def with_raw(dest, raw):
    """配了框架时 mirror(dest, raw)，没配时 minimal(dest, raw)。"""
    try:
        knowledge_source.framework_root()
    except knowledge_source.KnowledgeFrameworkNotFound:
        return minimal(dest, raw)
    return mirror(dest, raw)


def without_raw():
    """{环境变量: 值}：指向一个没有原件总库的临时框架（每个进程建一个，退出时删）。"""
    if not _NO_RAW:
        dest = Path(tempfile.mkdtemp(prefix='asg-framework-no-library-'))
        atexit.register(shutil.rmtree, dest, True)
        _NO_RAW.append(mirror(dest))
    return {knowledge_source.ENV_VAR: str(_NO_RAW[0])}
