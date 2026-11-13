"""Datasheet citations ``datasheet:<library path>#p<page>``, checked against the PDF itself.

A citation whose file cannot be found while the library is present, or whose page is
beyond the document, is wrong (FAIL). A cited value that the page text does not show
is listed for a person to check, never blocking: tables, units and scanned pages defeat
plain text search. Without the library or the poppler tools the citation is NOT_CHECKED,
with the reason. Locator text (table name, symbol) is not searched.
"""

import re
import shutil
import subprocess
from pathlib import Path

import knowledge_source

CITATION = re.compile(r'^datasheet:(.+)#p(\d+)$')
_pages, _texts = {}, {}


def parse(source):
    """(library path, page) of a datasheet citation, or None for anything else."""
    m = CITATION.match(source) if isinstance(source, str) else None
    return (m.group(1), int(m.group(2))) if m else None


def library_root():
    """The source library: the knowledge framework's 原件/ (HardwareWiki/raw); None when it is not there."""
    try:
        return knowledge_source.raw_root()
    except knowledge_source.KnowledgeFrameworkNotFound:
        return None


def locate(path, extra=()):
    """The cited file: under the library (a path such as Datasheet/<category>/…, an older raw/Datasheet/… or an absolute
    path), then a declared folder or file by name."""
    raw = library_root()
    path = path[len('raw/'):] if raw is not None and path.startswith('raw/') else path
    for base in ((raw,) if raw is not None else ()) + tuple(map(Path, extra)):
        base = base.expanduser()
        candidates = (base / path, base / Path(path).name) if base.is_dir() else (base,)
        for c in candidates:
            if c.is_file() and c.name == Path(path).name:
                return c
    return None


def library_present():
    return library_root() is not None


def page_count(pdf):
    if pdf not in _pages:
        tool = shutil.which('pdfinfo')
        out = subprocess.run([tool, str(pdf)], capture_output=True, text=True, timeout=60).stdout if tool else ''
        m = re.search(r'^Pages:\s+(\d+)', out, re.M)
        _pages[pdf] = int(m.group(1)) if m else None
    return _pages[pdf]


def page_text(pdf, page):
    key = (pdf, page)
    if key not in _texts:
        tool = shutil.which('pdftotext')
        _texts[key] = subprocess.run([tool, '-f', str(page), '-l', str(page), '-q', str(pdf), '-'],
                                     capture_output=True, text=True, timeout=60).stdout if tool else None
    return _texts[key]


def _shown(value, text):
    """A number appears on the page as written (30, 0.6, .6), in another SI prefix (2e-7 as 200 ns,
    0.45 as 450 mV) or as a percentage (0.2 as 20 %), not inside a longer number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return True
    scaled = [value * 10 ** (3 * k) for k in range(-4, 5)] + [value * 100]
    forms = {'%g' % float('%.6g' % v) for v in scaled} | {str(value)}
    forms |= {f[1:] for f in forms if f.startswith('0.')}
    text = text.replace(',', '.').replace('\u2212', '-')          # decimal comma, Unicode minus
    # A decimal may carry trailing zeros on the page (0.93 as 0.930); a whole number may not (30 is not 300).
    return any(re.search(r'(?<![\d.])%s%s(?![\d])' % (re.escape(f), '0*' if '.' in f else ''), text) for f in forms)


def check(path, page, values=(), extra=()):
    """{status: PASS|FAIL|NOT_CHECKED, reason, unshown: [values the page text does not show]}."""
    if path.startswith(('/', '~')):
        # R8 cited /Users/.../资料依据/原厂资料/NCP1343.pdf: the citation names the library file, not this machine's copy.
        return {'status': 'FAIL', 'reason': '手册 %s 写的是本机路径，要写知识库里的路径（Datasheet/<分类>/<子类>/<文件>）' % path,
                'unshown': [], 'not_library': True}
    pdf = locate(path, extra)
    if pdf is None:
        if not library_present():
            return {'status': 'NOT_CHECKED', 'reason': '找不到知识库，手册 %s 没核对' % path, 'unshown': []}
        return {'status': 'FAIL', 'reason': '手册 %s 不在知识库或声明的资料里' % path, 'unshown': []}
    if not shutil.which('pdfinfo'):
        return {'status': 'NOT_CHECKED', 'reason': '没有 pdfinfo（poppler），%s 的页码没核对' % path, 'unshown': []}
    pages = page_count(pdf)
    if pages is None:
        return {'status': 'FAIL', 'reason': '%s 读不出页数，不是可用的 PDF' % path, 'unshown': []}
    if not 1 <= page <= pages:
        return {'status': 'FAIL', 'reason': '%s 只有 %d 页，引用了第 %d 页' % (path, pages, page), 'unshown': []}
    flat = [v for x in values for v in (x if isinstance(x, (list, tuple)) else [x])]
    if not any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in flat):
        return {'status': 'PASS', 'reason': '', 'unshown': []}
    text = page_text(pdf, page)
    if text is None:
        return {'status': 'PASS', 'reason': '没有 pdftotext，%s 的数值没核对' % path, 'unshown': []}
    return {'status': 'PASS', 'reason': '', 'unshown': [v for v in flat if not _shown(v, text)]}


def check_source(source, values=(), extra=()):
    """check() for a ``datasheet:…#p<n>`` string; None when the source is not a datasheet citation."""
    cited = parse(source)
    return check(*cited, values, extra) if cited else None
