#!/usr/bin/env python3
"""Run one delivery from records to package in a fixed order: deliver.py <交付目录>.

Arguments come from <交付目录>/record/deliver.json, kept with the delivery and reused
each version:

  {"schema_version": 1,
   "prepare":  [["python3", "record/scripts/make_closure.py"]],          # optional, run in order
   "generate": {"command": ["python3", "record/scripts/replay.py", "--artifact-root", "{root}",
                            "--output-root", "{out}"], "schematic": "schematic"},
   "root":     "设计方案/board.kicad_sch",
   "verify":   ["--expected-pages", "8", "--reference-contract", "record/reference-input.json"],
   "inputs":   {"requirements": "/path/需求", "datasheets": "/path/资料"},
   "check_inputs": ["python3", "record/scripts/replay.py", "--artifact-root", "{root}",
                    "--output-root", "{out}", "--check-inputs"],             # optional
   "title": "报告标题"}                                                        # optional

{root} is the delivery folder and {out} a fresh empty directory. Commands run in the
delivery folder. A step continues only on a status in CONTINUE; CONDITIONAL and INCOMPLETE
are normal design states. Any other status, a missing result or a command error stops the
run. A run whose PDF has no matching record/visual-review.json stops after the checks
(exit 2, review pending); a review written on the step-4 PDF matches, so one run delivers.
The delivery evidence is written from this run's files and checked fresh before
packing. Exit 0 only when every step finished.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from schematic_layout.component_requirements import artifact_audit
from render_design_report import render_sha256
from check_delivery_freshness import LIB_ROW, evidence_sha256, snapshot_rows
import requirement_baseline

HERE = Path(__file__).resolve().parent
KICAD_FILES = ('*.kicad_sch', '*.kicad_pro', '*.kicad_prl', '*.kicad_sym', 'sym-lib-table', 'netlist.xml', 'schematic.pdf')
# Records a delivery folder never hashes as its own inputs.
NOT_INPUTS = {'record/manifest.json', 'record/delivery-evidence.json'}
# 设计方案/ is one KiCad project shared with the PCB stage (user 2026-11-13). The schematic's own files are the delivery's;
# the board (.kicad_pcb, .kicad_dru, sub-folders, its notes) and the local settings file (.kicad_prl) are not hashed, and
# the project file is hashed without its board-only section (check_delivery_freshness.evidence_sha256): a board edit
# never stales the schematic evidence, a net-class change does.
SCHEMATIC_INPUTS = ('*.kicad_sch', '*.kicad_sym', '*.kicad_pro', 'sym-lib-table', 'netlist.xml', 'schematic.pdf', 'BOM.csv')
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
    """Replace the schematic of the KiCad project in 设计方案/ with the freshly generated one. Other files (BOM.csv,
    the board and the PCB stage's files) stay, and sections of the old .kicad_pro the new one lacks (board rules,
    net classes) are carried over, so a new drawing never loses the board's settings."""
    if not source.is_dir() or not any(source.glob('*.kicad_sch')):
        raise StepFailed('出图：%s 里没有生成 .kicad_sch' % source)
    target.mkdir(exist_ok=True)
    kept = {p.name: json.loads(p.read_text(encoding='utf-8')) for p in target.glob('*.kicad_pro')}
    table = target / 'sym-lib-table'
    snapshot = snapshot_rows(table.read_text(encoding='utf-8')) if table.is_file() else []
    for pattern in KICAD_FILES:
        for old in target.glob(pattern):
            old.unlink()
    for new in source.iterdir():
        if new.is_file():
            shutil.copy2(new, target / new.name)
    if snapshot:     # the project's frozen library copy (库快照/) keeps its rows next to the new drawing's own
        own = [m.group(0).strip() for m in LIB_ROW.finditer(table.read_text(encoding='utf-8'))] if table.is_file() else []
        names = {re.search(r'\(name "([^"]*)"', r).group(1) for r in own}
        rows = own + [r for r in snapshot if re.search(r'\(name "([^"]*)"', r).group(1) not in names]
        table.write_text('(sym_lib_table\n  (version 7)\n' + ''.join('  %s\n' % r for r in rows) + ')\n', encoding='utf-8')
    for name, old in kept.items():
        path = target / name
        if path.is_file():
            project = json.loads(path.read_text(encoding='utf-8'))
            missing = {k: v for k, v in old.items() if k not in project}
            if missing:
                project.update(missing)
                path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def copy_gates(gates, root):
    """KiCad exports go to 设计方案/, gate results to record/, per-page geometry to record/evidence/."""
    record = root / 'record'
    copied = []
    for name in ('netlist.xml', 'schematic.pdf'):
        if (gates / name).is_file():
            shutil.copy2(gates / name, root / '设计方案' / name)
            copied.append('设计方案/' + name)
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
    design = root / '设计方案'
    schematic = sorted({p.relative_to(root).as_posix() for pattern in SCHEMATIC_INPUTS for p in design.glob(pattern)
                        if p.is_file()}) if design.is_dir() else []
    inputs = [p for p in schematic + listed('设计资料') + listed('record')
              if p not in outputs and p not in NOT_INPUTS]
    roles = {'netlist': ['设计方案/netlist.xml'], 'erc': ['record/erc.json'], 'render': ['设计方案/schematic.pdf'],
             'geometry': [p for p in outputs if p.startswith('record/evidence/geometry-')]}
    for role, path in (('visual_review', 'record/visual-review.json'), ('delta', 'record/design-change.json')):
        if path in outputs:
            roles[role] = [path]
    return {'schema_version': 1, 'root': schematic_root,
            'inputs': {p: evidence_sha256(root / p) for p in inputs},
            'outputs': {p: sha256(root / p) for p in outputs}, 'roles': roles}


def review_matches(path, pdf):
    """record/visual-review.json is a finished review of this PDF (same rendered content, export time ignored)."""
    try:
        review = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return False
    return isinstance(review, dict) and review.get('status') == 'REVIEWED' and review.get('pdf_sha256') == render_sha256(pdf)


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


def deliver(root, log=print, for_review=False):
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

        out = work / 'generate'
        run(fill(config['generate']['command'], root, out), root, '出图')
        copy_schematic(out / config['generate']['schematic'], root / '设计方案')
        step('出图', 'DONE')

        gates = work / 'gates'
        subprocess.run(skill('verify_schematic.py', root / config['root'], '--intent', intent, '--out', gates, *declared,
                             *fill(config.get('verify') or [], root, work / 'verify')), cwd=root, capture_output=True)
        if not (gates / 'summary.json').is_file():
            raise StepFailed('自动检查：没有生成 summary.json')
        written += copy_gates(gates, root)
        step('自动检查', status_of(gates / 'summary.json'))

        # The visual review reads this run's PDF. Drawing is deterministic, so a review written on the PDF of the
        # step-4 check matches this export and the run goes on in one pass; without a matching review the run stops
        # here, not at the report (calibration board 2026-11-07: delivery took two full runs).
        pdf = root / '设计方案' / 'schematic.pdf'
        reviewed = pdf.is_file() and review_matches(record / 'visual-review.json', pdf)
        if for_review or (pdf.is_file() and not reviewed):
            log('图面审阅：按 设计方案/schematic.pdf 写 record/visual-review.json（pdf_sha256 %s），再跑 deliver.py'
                % render_sha256(pdf) if pdf.is_file() else '图面审阅：本次没有导出 PDF')
            if for_review:
                return 0, steps, None
            steps.append({'step': '图面审阅', 'status': 'PENDING'})
            log('%-12s %s' % ('图面审阅', 'PENDING'))
            return 2, steps, None

        # The knowledge-gap list is extracted from this version's records (SKILL.md 能力目标 7); the report prints it.
        run(skill('knowledge_gaps.py', root, *declared), root, '知识缺口清单')
        written.append('record/knowledge-gaps.json')
        step('知识缺口清单', 'DONE')

        # The requirement baseline later stages read (they do not read record/): clauses plus decided clarifications.
        if (record / 'requirements.json').is_file():
            requirement_baseline.main([str(root)])
            written.append(requirement_baseline.NAME)
            step('需求基线', 'DONE')

        notes = record / 'notes.json'
        report = subprocess.run(skill('render_design_report.py', root, *(['--notes', notes] if notes.is_file() else []),
                                      *(['--title', config['title']] if config.get('title') else [])),
                                cwd=root, capture_output=True, text=True)
        if report.returncode:      # the report is written, but the records it was made from have problems
            log('\n'.join(l for l in (report.stdout + report.stderr).splitlines() if l.startswith('PROBLEM'))[:2000])
        written.append('设计报告.md')
        step('生成报告', 'FAIL' if report.returncode else 'DONE')

        extra = [p.relative_to(root).as_posix() for p in (root / '设计方案' / 'BOM.csv', record / 'visual-review.json')
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
        to_file = [line.split(' ', 1)[1] for line in packed.stdout.splitlines() if line.startswith('TO_FILE: ')]
        if to_file:
            log('手册待入库（本项目用到、知识库还没有，设计完成后提示用户复制进知识库）：\n' + '\n'.join(to_file))
            # A reminder for the user, not a step that can stop the run (Matrix 2026-11-07 #25: exit 1 after pack PASS).
            steps.append({'step': '手册待入库', 'status': '%d 份' % len(to_file)})
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
    ap.add_argument('--for-review', action='store_true',
                    help='stop after the automatic checks even if a review matches: the PDF is exported for the visual review')
    args = ap.parse_args(argv)
    code, _, _ = deliver(args.delivery, for_review=args.for_review)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
