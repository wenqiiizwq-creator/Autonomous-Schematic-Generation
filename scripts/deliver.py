#!/usr/bin/env python3
"""Run one delivery from records to package in a fixed order: deliver.py <交付目录>.

Arguments come from <交付目录>/record/deliver.json, kept with the delivery and reused
each version:

  {"schema_version": 1,
   "prepare":  [["python3", "record/scripts/make_closure.py"]],          # optional, run in order
   "generate": {"command": ["python3", "record/scripts/replay.py", "--artifact-root", "{root}",
                            "--output-root", "{out}"], "schematic": "schematic"},
   "root":     "原理图/board.kicad_sch",
   "verify":   ["--expected-pages", "8", "--reference-contract", "record/reference-input.json"],
   "inputs":   {"requirements": "/path/需求", "datasheets": "/path/资料", "previous": "/path/上一版"},
   "check_inputs": ["python3", "record/scripts/replay.py", "--artifact-root", "{root}",
                    "--output-root", "{out}", "--check-inputs"],             # optional
   "title": "报告标题"}                                                        # optional

{root} is the delivery folder and {out} a fresh empty directory. Commands run in the
delivery folder. A step continues only on a status in CONTINUE; CONDITIONAL and INCOMPLETE
are normal design states. Any other status, a missing result or a command error stops the
run. The delivery evidence is written from this run's files and checked fresh before
packing. Exit 0 only when every step finished.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from schematic_layout.component_requirements import artifact_audit

HERE = Path(__file__).resolve().parent
KICAD_FILES = ('*.kicad_sch', '*.kicad_pro', '*.kicad_prl', '*.kicad_sym', 'sym-lib-table', 'netlist.xml', 'schematic.pdf')
# Records a delivery folder never hashes as its own inputs.
NOT_INPUTS = {'record/manifest.json', 'record/delivery-evidence.json'}
# Step results that let the run go on; anything else (FAIL, STALE_OR_INVALID, none) stops it.
CONTINUE = {'PASS', 'DONE', 'CONDITIONAL', 'INCOMPLETE', 'AUTOMATED_PASS', 'FRESH'}


class StepFailed(Exception):
    pass


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def status_of(path):
    path = Path(path)
    return json.loads(path.read_text(encoding='utf-8')).get('status') if path.is_file() else None


def fill(args, root, out):
    return [str(a).replace('{root}', str(root)).replace('{out}', str(out)) for a in args]


def run(cmd, root, label):
    result = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    if result.returncode:
        tail = (result.stdout + result.stderr).strip().splitlines()[-5:]
        raise StepFailed('%s：命令出错（退出码 %d）：%s' % (label, result.returncode, ' | '.join(tail)))
    return result


def skill(script, *args):
    return [sys.executable, str(HERE / script), *map(str, args)]


def copy_schematic(source, target):
    """Replace the KiCad project in 原理图/ with the freshly generated one; other files (BOM.csv) stay."""
    if not source.is_dir() or not any(source.glob('*.kicad_sch')):
        raise StepFailed('出图：%s 里没有生成 .kicad_sch' % source)
    for pattern in KICAD_FILES:
        for old in target.glob(pattern):
            old.unlink()
    for new in source.iterdir():
        if new.is_file():
            shutil.copy2(new, target / new.name)


def copy_gates(gates, root):
    """KiCad exports go to 原理图/, gate results to record/, per-page geometry to record/evidence/."""
    record = root / 'record'
    copied = []
    for name in ('netlist.xml', 'schematic.pdf'):
        if (gates / name).is_file():
            shutil.copy2(gates / name, root / '原理图' / name)
            copied.append('原理图/' + name)
    for path in sorted(gates.glob('*.json')):
        if path.name == 'design-closure.json':
            continue        # the run's own closure audit step already wrote record/design-closure-audit.json
        shutil.copy2(path, record / path.name)
        copied.append('record/' + path.name)
    evidence = record / 'evidence'
    evidence.mkdir(exist_ok=True)
    for old in evidence.glob('geometry-*.json'):
        old.unlink()
    for path in sorted((gates / 'geometry').glob('*.json')):
        shutil.copy2(path, evidence / ('geometry-' + path.name))
        copied.append('record/evidence/geometry-' + path.name)
    return copied


def build_evidence(root, schematic_root, outputs):
    """delivery-evidence.json from this run: the files it wrote are outputs, everything else it read is an input."""
    root = Path(root)
    outputs = sorted(set(outputs))
    def listed(folder):
        base = root / folder
        return [p.relative_to(root).as_posix() for p in sorted(base.rglob('*'))
                if p.is_file() and '__pycache__' not in p.parts and not p.name.startswith('.')] if base.is_dir() else []
    inputs = [p for p in listed('原理图') + listed('设计资料') + listed('record')
              if p not in outputs and p not in NOT_INPUTS]
    roles = {'netlist': ['原理图/netlist.xml'], 'erc': ['record/erc.json'], 'render': ['原理图/schematic.pdf'],
             'geometry': [p for p in outputs if p.startswith('record/evidence/geometry-')]}
    for role, path in (('visual_review', 'record/visual-review.json'), ('delta', 'record/design-change.json')):
        if path in outputs:
            roles[role] = [path]
    return {'schema_version': 1, 'root': schematic_root,
            'inputs': {p: sha256(root / p) for p in inputs},
            'outputs': {p: sha256(root / p) for p in outputs}, 'roles': roles}


def load_config(root):
    path = root / 'record' / 'deliver.json'
    if not path.is_file():
        raise StepFailed('缺少 record/deliver.json：写明出图命令、根图、验证参数和打包输入（格式见脚本说明）')
    config = json.loads(path.read_text(encoding='utf-8'))
    problems = [k for k in ('root', 'inputs') if not config.get(k)]
    generate = config.get('generate')
    if not (isinstance(generate, dict) and generate.get('command') and generate.get('schematic')):
        problems.append('generate.command/schematic')
    if config.get('schema_version') != 1 or problems:
        raise StepFailed('record/deliver.json 不完整：%s' % ('、'.join(problems) or 'schema_version 要为 1'))
    return config


def deliver(root, log=print):
    root = Path(root).resolve()
    record = root / 'record'
    steps = []
    def step(label, status):
        steps.append({'step': label, 'status': status})
        log('%-12s %s' % (label, status))
        if status not in CONTINUE:
            raise StepFailed('%s：%s，停在这一步' % (label, status or '没有写出结果'))
    work = Path(tempfile.mkdtemp(prefix='asg-deliver-'))
    try:
        config = load_config(root)
        intent = record / 'electrical-intent.json'
        declared = [a for k, v in config['inputs'].items() for a in ('--input', '%s=%s' % (k, v))]
        for i, cmd in enumerate(config.get('prepare') or [], 1):
            run(fill(cmd, root, work / ('prepare-%d' % i)), root, '准备 %d' % i)
            step('准备 %d' % i, 'DONE')

        # Preparation projects the single source into IR/BOM. This check is
        # read-only and runs before generation; verification checks native exports.
        performance = artifact_audit(root, json.loads(intent.read_text(encoding='utf-8')))
        if performance['status'] != 'NOT_CHECKED':
            step('器件性能预检', performance['status'])

        audit = record / 'design-closure-audit.json'
        audit.unlink(missing_ok=True)
        subprocess.run(skill('audit_design_closure.py', record / 'design-closure.json', '--intent', intent,
                             '--artifact-root', root, *declared, '--out', audit), cwd=root, capture_output=True)
        step('待办审计', status_of(audit))
        written = ['record/design-closure-audit.json']

        preflight = record / 'design-preflight.json'
        contract = record / 'change-contract.json'
        def preflight_check(label, out, *extra):
            out.unlink(missing_ok=True)
            subprocess.run(skill('verify_design_preflight.py', preflight, '--contract', contract, '--root', root,
                                 *extra, '--out', out), cwd=root, capture_output=True)
            step(label, status_of(out))
            return 'record/' + out.name
        if preflight.is_file() != contract.is_file():
            step('生成前预检', 'FAIL')     # one of the two alone is an unfinished record, not a design without a revision
        if preflight.is_file() and contract.is_file():
            written.append(preflight_check('生成前预检', record / 'preflight-before.json', '--before-generation'))

        out = work / 'generate'
        run(fill(config['generate']['command'], root, out), root, '出图')
        copy_schematic(out / config['generate']['schematic'], root / '原理图')
        step('出图', 'DONE')

        gates = work / 'gates'
        subprocess.run(skill('verify_schematic.py', root / config['root'], '--intent', intent, '--out', gates, *declared,
                             *fill(config.get('verify') or [], root, work / 'verify')), cwd=root, capture_output=True)
        if not (gates / 'summary.json').is_file():
            raise StepFailed('自动检查：没有生成 summary.json')
        written += copy_gates(gates, root)
        step('自动检查', status_of(gates / 'summary.json'))

        if preflight.is_file() and contract.is_file():
            written.append(preflight_check('交付预检', record / 'preflight-delivery.json'))

        notes = record / 'notes.json'
        report = subprocess.run(skill('render_design_report.py', root, *(['--notes', notes] if notes.is_file() else []),
                                      *(['--title', config['title']] if config.get('title') else [])),
                                cwd=root, capture_output=True, text=True)
        if report.returncode:      # the report is written, but the records it was made from have problems
            log('\n'.join(l for l in (report.stdout + report.stderr).splitlines() if l.startswith('PROBLEM'))[:2000])
        written.append('设计报告.md')
        step('生成报告', 'FAIL' if report.returncode else 'DONE')

        extra = [p.relative_to(root).as_posix() for p in (root / '原理图' / 'BOM.csv', record / 'visual-review.json')
                 if p.is_file()]
        evidence = build_evidence(root, config['root'], written + extra)
        (record / 'delivery-evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n',
                                                       encoding='utf-8')
        step('交付证据', 'DONE')

        fresh = subprocess.run(skill('check_delivery_freshness.py', record / 'delivery-evidence.json'),
                               cwd=root, capture_output=True, text=True)
        step('证据新鲜度', json.loads(fresh.stdout).get('status') if fresh.stdout.strip().startswith('{') else None)

        packed = subprocess.run(skill('pack_design.py', root, *declared), cwd=root, capture_output=True, text=True)
        if packed.returncode:
            log('\n'.join((packed.stdout + packed.stderr).strip().splitlines()[-8:]))
        step('打包', 'PASS' if packed.returncode == 0 else 'FAIL')
        if config.get('check_inputs'):
            run(fill(config['check_inputs'], root, work / 'check-inputs'), root, '输入核对')
            step('输入核对', 'PASS')
        return 0, steps, None
    except StepFailed as failure:
        log(str(failure))
        return 1, steps, str(failure)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('delivery', type=Path)
    args = ap.parse_args(argv)
    code, _, _ = deliver(args.delivery)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
