"""knowledge_source.py and the framework-reading half of guideline_criteria.py: where the framework is found, what
identity() records, and that criteria assemble from the framework's registries. Tests that need the real framework
skip when none is configured; the others build a small framework in a temporary directory."""
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import guideline_criteria as g
import knowledge_source as ks

ENV = ks.ENV_VAR
DERATING = ks.DERATING_DIR


def real_framework():
    """The configured framework, or None (the test then skips)."""
    try:
        return ks.framework_root()
    except ks.KnowledgeFrameworkNotFound:
        return None


REAL = real_framework()
needs_framework = unittest.skipUnless(REAL, '没有配置知识框架（环境变量 %s 或 .knowledge-framework）' % ENV)


def make_framework(root, registries=('G02',), criteria_per_registry=2):
    """A small framework: 知识/ with the seven components, 索引/, and a registry subset with a vocabulary."""
    root = Path(root)
    for name in ks.COMPONENTS:
        (root / '知识' / name).mkdir(parents=True)
        (root / '知识' / name / '条目.md').write_text('# %s\n' % name, encoding='utf-8')
    (root / '索引').mkdir()
    for name in ('索引/条目总表.md', '索引/准则支撑表.md', '原件勘误.md', '条目规范.md'):
        (root / name).write_text('# %s\n' % name, encoding='utf-8')
    registry = root / '知识/设计准则/准则登记'
    registry.mkdir(parents=True)
    vocab = {'version': '1', 'default_baseline': 'base',
             'baselines': [{'name': 'base', 'title': '基线'}],
             'circuit_types': [{'name': 'power', 'title': '电源'}],
             'device_kinds': [{'name': 'resistor', 'title': '电阻'}]}
    (registry / '词表.json').write_text(json.dumps(vocab, ensure_ascii=False), encoding='utf-8')
    for spec in registries:
        rules = [{'id': '%s-%03d' % (spec, n + 1), 'title': 'rule %d' % n, 'spec': spec, 'version': '1',
                  'status': 'active', 'nature': 'shall', 'applies_when': {'board': True}, 'asg_action': 'do',
                  'sr_check': 'check', 'closing_stage': 'schematic',
                  'source': [{'document': 'doc', 'edition': '1', 'clause': '1', 'page': '1'}]}
                 for n in range(criteria_per_registry)]
        (registry / ('%s_准则登记.json' % spec)).write_text(
            json.dumps({'spec': spec, 'version': '1', 'criteria': rules}, ensure_ascii=False), encoding='utf-8')
    return root


class Locating(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.fw = make_framework(self.tmp / 'fw')

    def test_environment_variable_names_the_framework(self):
        with mock.patch.dict(os.environ, {ENV: str(self.fw)}):
            self.assertEqual(ks.framework_root(), self.fw)
            self.assertEqual(ks.knowledge_dir(), self.fw / '知识')
            self.assertEqual(ks.index_dir(), self.fw / '索引')
            self.assertEqual(ks.registry_dir(), self.fw / '知识/设计准则/准则登记')
            self.assertEqual(ks.vocabulary_path(), self.fw / '知识/设计准则/准则登记/词表.json')
            self.assertEqual(ks.derating_path().name, '降额值.json')
            self.assertEqual(ks.errata_path(), self.fw / '原件勘误.md')

    def test_local_file_names_the_framework_and_environment_wins(self):
        local = self.tmp / ks.LOCAL_FILE_NAME
        local.write_text('\n%s\n' % self.fw, encoding='utf-8')
        other = make_framework(self.tmp / 'other')
        with mock.patch.object(ks, 'SKILL_ROOT', self.tmp), mock.patch.dict(os.environ, {ENV: ''}):
            self.assertEqual(ks.framework_root(), self.fw)
            with mock.patch.dict(os.environ, {ENV: str(other)}):
                self.assertEqual(ks.framework_root(), other)

    def test_not_found_says_how_to_set_it(self):
        with mock.patch.object(ks, 'SKILL_ROOT', self.tmp), mock.patch.dict(os.environ, {ENV: ''}):
            with self.assertRaises(ks.KnowledgeFrameworkNotFound) as caught:
                ks.framework_root()
        self.assertIsInstance(caught.exception, ValueError)
        self.assertIn(ENV, str(caught.exception))
        self.assertIn(ks.LOCAL_FILE_NAME, str(caught.exception))

    def test_a_directory_without_knowledge_and_index_is_refused(self):
        (self.tmp / 'empty').mkdir()
        with mock.patch.dict(os.environ, {ENV: str(self.tmp / 'empty')}):
            with self.assertRaisesRegex(ks.KnowledgeFrameworkNotFound, '知识'):
                ks.framework_root()

    def test_importing_resolves_nothing(self):
        """--help must work with no framework configured (a copy of the scripts sits where no .knowledge-framework is)."""
        import subprocess
        scripts = self.tmp / 'skill' / 'scripts'
        scripts.mkdir(parents=True)
        for name in ('knowledge_source.py', 'guideline_criteria.py'):
            shutil.copy(SCRIPTS / name, scripts / name)
        env = {k: v for k, v in os.environ.items() if k != ENV}
        run = subprocess.run([sys.executable, str(scripts / 'guideline_criteria.py'), '--help'], env=env,
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        run = subprocess.run([sys.executable, str(scripts / 'guideline_criteria.py'), 'check'], env=env,
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertIn(ENV, run.stderr)


class SmallFramework(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.fw = make_framework(self.tmp / 'fw')
        patch = mock.patch.dict(os.environ, {ENV: str(self.fw), 'GUIDELINE_CRITERIA': ''})
        patch.start()
        self.addCleanup(patch.stop)

    def test_identity_is_the_read_date(self):
        ident = ks.identity()
        self.assertEqual(set(ident), {'read_date'})
        self.assertRegex(ident['read_date'], r'^\d{4}-\d{2}-\d{2}$')
        self.assertIn(ident['read_date'], ks.label(ident))

    def test_load_assembles_the_registry_subset(self):
        library = g.load()
        self.assertEqual([r['id'] for r in library['criteria']], ['G02-001', 'G02-002'])
        self.assertEqual(g.bundle_errors(library), [])
        self.assertEqual(library['default_baseline'], 'base')

    def test_build_follows_the_registries(self):
        registry, vocab = ks.registry_dir(), ks.vocabulary_path()
        built = g.build(registry, vocabulary_path=vocab)
        self.assertEqual(built, g.build(registry, vocab))
        second = make_framework(self.tmp / 'fw2', registries=('G02', 'G03'))
        more = g.build(second / '知识/设计准则/准则登记', vocabulary_path=second / '知识/设计准则/准则登记/词表.json')
        self.assertNotEqual(more['criteria'], built['criteria'])
        self.assertEqual(g.build(second / '知识/设计准则/准则登记',
                                 vocabulary_path=second / '知识/设计准则/准则登记/词表.json'), more)

    def test_load_follows_a_changed_registry_and_refuses_a_broken_one(self):
        before = g.load()
        path = self.fw / '知识/设计准则/准则登记/G02_准则登记.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        data['criteria'][0]['title'] = 'renamed'
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        after = g.load()
        self.assertNotEqual(before['criteria'], after['criteria'])
        data['criteria'][0]['status'] = 'nonsense'
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'status'):
            g.load()

    def test_load_returns_a_copy(self):
        g.load()['criteria'].clear()
        self.assertEqual(len(g.load()['criteria']), 2)

    def test_explicit_path_is_read_as_is(self):
        path = self.tmp / 'bundle.json'
        path.write_text(g.dump(g.load()), encoding='utf-8')
        self.assertEqual(g.load(path), g.load())

    def test_environment_substitution_needs_test_mode(self):
        with mock.patch.dict(os.environ, {'GUIDELINE_CRITERIA': str(self.tmp / 'x.json')}):
            os.environ.pop('GUIDELINE_CRITERIA_TESTING', None)
            with self.assertRaisesRegex(ValueError, 'test-only'):
                g.load()


@needs_framework
class RealFramework(unittest.TestCase):
    def test_framework_has_the_paths_the_skill_reads(self):
        for path in (ks.knowledge_dir(), ks.index_dir(), ks.guideline_dir(), ks.registry_dir()):
            self.assertTrue(path.is_dir(), path)
        for path in (ks.vocabulary_path(), ks.derating_path(), ks.commodity_path(), ks.errata_path(),
                     ks.entry_spec_path()):
            self.assertTrue(path.is_file(), path)

    def test_typical_circuit_file_names_are_unique_across_domains(self):
        stems = [p.stem for p in (ks.knowledge_dir() / '典型电路').rglob('*.md') if p.name != 'README.md']
        self.assertEqual(sorted({s for s in stems if stems.count(s) > 1}), [])

    def test_assembled_criteria_pass_the_bundle_checks(self):
        library = g.load()
        self.assertEqual(g.bundle_errors(library), [])
        self.assertTrue(library['criteria'])
        self.assertTrue(library['engineering_values'])
        self.assertIn(library['default_baseline'], library['vocabulary']['baselines'])

    def test_shared_versions_records_the_read_date_and_derating_version(self):
        self.assertEqual(set(g.shared_versions()), {'derating_version', 'read_date'})
        self.assertRegex(g.shared_label(), r'^设计准则（\d{4}-\d{2}-\d{2} 读取），降额 v\S+$')

    def test_vocabulary_and_floors_come_from_the_framework(self):
        self.assertEqual(g.vocabulary()['vocabulary']['baselines'], g.load()['vocabulary']['baselines'])
        self.assertTrue(g.vocabulary_titles('device_kinds'))
        self.assertIn('chip_resistor', g.commodity_floors())


if __name__ == '__main__':
    unittest.main()
