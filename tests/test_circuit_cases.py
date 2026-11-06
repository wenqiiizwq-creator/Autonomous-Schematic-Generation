"""电路评测集与 ASG 的接口：只给需求，答案不进工作目录。"""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
import eval_set  # noqa: E402

spec = importlib.util.spec_from_file_location('asg_circuit_cases', ROOT / 'evals/circuit_cases/run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)


def local_release():
    import shutil
    import tempfile
    temporary = tempfile.TemporaryDirectory(prefix='eval-release-')
    release = Path(temporary.name)
    manifest = json.loads((ROOT / 'shared-release.json').read_text(encoding='utf-8'))
    manifest.update(inputs={}, auxiliary={})
    for name in manifest['payload']:
        target = release / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    (release / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    return temporary, release


_RELEASE_TEMP, RELEASE = local_release()


@unittest.skipUnless(eval_set.available(), '电路评测集不在本机')
class Prepare(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.out = Path(tmp.name) / 'job'

    def prepare(self, case='iio-can'):
        import argparse
        return run.cmd_prepare(argparse.Namespace(case=case, out=self.out, guideline_release=RELEASE))

    def test_gives_requirements_only(self):
        self.prepare()
        self.assertEqual(sorted(p.name for p in self.out.iterdir()), ['run-context.json', '任务.md', '需求.md'])
        task = (self.out / '任务.md').read_text(encoding='utf-8')
        self.assertIn('不要读取', task)
        evalset = run.tool()
        case = {c['id']: c for _, c in evalset.load_cases()}['iio-can']
        text = (self.out / '需求.md').read_text(encoding='utf-8')
        for variant_part in ('TCAN1042', 'ESD2CAN', 'MF-R005'):
            self.assertNotIn(variant_part, text)
        self.assertTrue(case['test_points'])

    def test_refuses_non_empty_directory_and_sr_only_case(self):
        self.out.mkdir()
        (self.out / 'x').write_text('')
        with self.assertRaises(SystemExit):
            self.prepare()
        with self.assertRaises(SystemExit):
            self.prepare('evm-plabs-sar')

    def test_requirements_of_every_asg_case_carry_no_part_number_of_its_answer(self):
        evalset = run.tool()
        import xml.etree.ElementTree as ET
        for path, case in evalset.load_cases():
            if 'ASG' not in case['skills'] or not case['variants']:
                continue
            text = (path.parent / '需求.md').read_text(encoding='utf-8')
            for variant in case['variants'].values():
                if 'netlist' not in variant:
                    continue
                for comp in ET.parse(path.parent / variant['netlist']).getroot().find('components'):
                    value = comp.find('value').text or ''
                    if comp.get('ref')[0] in 'UQ' and len(value) >= 6:
                        self.assertNotIn(value, text, f"{case['id']} {comp.get('ref')}")


if __name__ == '__main__':
    unittest.main()
