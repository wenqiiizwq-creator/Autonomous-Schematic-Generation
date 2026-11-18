#!/usr/bin/env python3
"""Run the tests a change needs: python3 tests/run.py [--all | --fast].

The drawing tests below build sheets and export them with KiCad: most of the suite's time, and they say nothing
about a change to a rule or a document. Without an option they run only when the working tree
(against HEAD, untracked files included) touches drawing code: scripts/schematic_layout/, a script a drawing test
imports, a drawing test or tests/fixtures/. --all runs everything (a KiCad version change, or when unsure); --fast
never runs them.
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
ROOT = TESTS.parent
DRAWING = '''drawing_recipes native_circle_controls recipe_rail_diagnostics external_supply_native
native_geometry_context verify_schematic schematic_generation spacing_and_blocks root recipe_rail_roles text_ink
swapped_labels wire_envelope native_semicircle_controls four_way_junction boundary_nets symbol_integrity page_fit
shared_terminals native_general_arc filtered_supply_native_qualification name_run_steps compact_presentation'''.split()


def drawing_code():
    """Paths (relative to the skill) whose change calls for the drawing tests."""
    paths = {'tests/test_%s.py' % name for name in DRAWING}
    for name in DRAWING:
        for module in re.findall(r'^(?:import|from) (\w+)', (TESTS / ('test_%s.py' % name)).read_text(encoding='utf-8'), re.M):
            paths.update(p for p in ('scripts/%s.py' % module, 'tests/%s.py' % module) if (ROOT / p).is_file())
    return paths


def touched():
    out = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, capture_output=True, text=True)
    if out.returncode:
        return None
    return {line[3:].split(' -> ')[-1].strip('"') for line in out.stdout.splitlines()}


def main(argv):
    missing = [name for name in DRAWING if not (TESTS / ('test_%s.py' % name)).is_file()]
    if missing:
        sys.exit('tests/run.py 的 DRAWING 里没有对应文件：%s' % '、'.join(missing))
    if argv not in ([], ['--all'], ['--fast']):
        sys.exit(__doc__)
    changed = touched()
    code = drawing_code()
    hit = None if changed is None else sorted(p for p in changed if p in code or p.startswith(('scripts/schematic_layout/', 'tests/fixtures/')))
    everything = argv == ['--all'] or (argv == [] and (hit is None or bool(hit)))
    if everything:
        reason = '--all' if argv else '读不到 git 状态' if hit is None else '改动涉及画图代码：' + '、'.join(hit[:5])
        print('全部测试（%s）' % reason, file=sys.stderr)
    else:
        print('不跑 %d 个画图测试文件（改动不涉及画图代码；全部测试用 --all）' % len(DRAWING), file=sys.stderr)
    skip = set() if everything else {'test_%s' % name for name in DRAWING}

    def keep(suite):
        kept = unittest.TestSuite()
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                kept.addTest(keep(item))
            elif type(item).__module__ not in skip:
                kept.addTest(item)
        return kept
    result = unittest.TextTestRunner().run(keep(unittest.defaultTestLoader.discover(str(TESTS))))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
