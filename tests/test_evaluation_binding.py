"""评测运行器的本地功能约定：显式绑定、记录身份、缺 E 单独 skip。"""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bound_case_runner', ROOT / 'evals/circuit_cases/run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_missing_external_set_is_reported_separately(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv('CIRCUIT_EVAL_SET', str(tmp_path / 'missing'))
    with pytest.raises(SystemExit) as stop:
        runner.tool()
    assert stop.value.code == 0
    report = json.loads(capsys.readouterr().out)
    assert report['status'] == 'skip'
    assert report['scope'] == 'external_evaluation'


def test_binding_receives_the_explicit_release_and_skill(monkeypatch):
    calls = []
    fake = SimpleNamespace(binding=SimpleNamespace(context=lambda *args: calls.append(args) or {'selected': 1}))
    monkeypatch.setattr(runner.eval_set, 'tool', lambda: fake)
    assert runner.eval_set.context(Path('/explicit/package'), ROOT) == {'selected': 1}
    assert calls == [(Path('/explicit/package'), runner.eval_set.root(), ROOT)]


def synthetic(monkeypatch, tmp_path):
    path = tmp_path / 'data' / 'case.json'
    path.parent.mkdir()
    (path.parent / '需求.md').write_text('只含需求', encoding='utf-8')
    case = dict(id='simple', title='simple', family='local', skills=['ASG', 'SR'],
                circuit_types=['CAN'], variants={'r1': {'netlist': 'r1.xml'}})
    identity = {'guidelines': {'library_version': 'test', 'shared_sha256': 'fixed', 'fingerprint_format': 'v2'},
                'eval_set': {'head': 'data-head', 'workspace_sha256': 'actual-dirty-data'},
                'skill': {'head': 'skill-head', 'workspace_sha256': 'actual-dirty-skill'}}
    fake = SimpleNamespace(load_cases=lambda: [(path, case)], check_case=lambda *args: [],
                           binding=SimpleNamespace(release_context=lambda release: ({}, identity['guidelines']),
                                                   case_inputs=lambda p: {'case.json': 'case-hash', '需求.md': 'req-hash'}))
    calls = []
    monkeypatch.setattr(runner, 'tool', lambda: fake)
    monkeypatch.setattr(runner.eval_set, 'context', lambda *args: calls.append(args) or identity.copy())
    return fake, identity, calls


def test_prepare_captures_identity_without_disclosing_answers(monkeypatch, tmp_path):
    _, identity, calls = synthetic(monkeypatch, tmp_path)
    args = SimpleNamespace(case='simple', out=tmp_path / 'out', guideline_release=tmp_path / 'chosen')
    runner.cmd_prepare(args)
    record = json.loads((args.out / 'run-context.json').read_text())
    assert record['skill_commit'] == 'skill-head'
    assert record['evaluation']['eval_set'] == identity['eval_set']
    assert record['evaluation']['guidelines'] == identity['guidelines']
    assert record['evaluation']['case_inputs']['case.json'] == 'case-hash'
    assert calls == [(args.guideline_release, ROOT)]
    assert sorted(p.name for p in args.out.iterdir()) == ['run-context.json', '任务.md', '需求.md']
    assert 'test_points' not in (args.out / 'run-context.json').read_text()
