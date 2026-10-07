"""Byte-preserving Value edits with frozen hierarchy and native change proof."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

from .sexpr import parse, all_nodes, value
from .project_audit import audit_project, _instance
from .native import find_cli
from .design_change import verify_change

TOKEN = re.compile(r'\s+|;[^\n]*|\(|\)|"(?:\\.|[^"\\])*"|[^\s();"]+')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def child_spans(text):
    """Immediate list children of a validated root, without reserializing it."""
    parse(text)
    depth, start = 0, None
    for token in TOKEN.finditer(text):
        if token.group() == '(':
            depth += 1
            if depth == 2:
                start = token.start()
        elif token.group() == ')':
            if depth == 2:
                yield start, token.end()
            depth -= 1


def frozen_files(root, audit):
    files = dict(audit['file_sha256'])
    project = root.with_suffix('.kicad_pro')
    if project.exists():
        files[project.name] = digest(project.read_bytes())
    return files


def prepare(root, contract):
    root = Path(root).resolve()
    if (set(contract) != {'schema_version', 'baseline_files', 'changes'}
            or contract['schema_version'] != 1):
        raise ValueError('Expected schema_version, baseline_files and changes only')
    audit = audit_project(root)
    if audit['status'] != 'PASS':
        raise ValueError('Hierarchy/annotation must be complete before editing: ' + json.dumps(audit['errors'] + audit['coverage_gaps']))
    files = frozen_files(root, audit)
    if contract['baseline_files'] != files:
        raise ValueError('Frozen file hashes do not match baseline')
    changes = contract['changes']
    if not isinstance(changes, dict) or not changes:
        raise ValueError('No Value changes requested')
    for ref, c in changes.items():
        if (not isinstance(ref, str) or not ref or ref.startswith('#') or not isinstance(c, dict)
                or set(c) != {'before', 'after'} or any(not isinstance(x, str) or not x.strip() or any(ord(ch) < 32 or ord(ch) == 127 for ch in x) for x in c.values())
                or c['before'] == c['after']):
            raise ValueError('Each physical ref needs distinct nonempty before/after Value strings')
    pages = {}
    for page in audit['pages']:
        pages.setdefault(page['path'], []).append(page['instance'])
    result, found, edits = {}, set(), []
    for filename, instances in pages.items():
        text = (root.parent / filename).read_bytes().decode('utf-8')
        replacements = []
        for a, b in child_spans(text):
            block = text[a:b]; symbol = parse(block)
            if symbol[0] != 'symbol':
                continue
            refs = {str(value(_instance(symbol, audit['project'], context) or [], 'reference')) for context in instances}
            selected = refs & changes.keys()
            if not selected:
                continue
            # A shared file edit affects all instances, including other projects.
            projects = all_nodes(next(iter(all_nodes(symbol, 'instances')), []), 'project')
            contexts = [p for project in projects for p in all_nodes(project, 'path')]
            if len(instances) != 1 or len(refs) != 1 or len(contexts) != 1:
                raise ValueError('Shared or multi-project symbol cannot be edited by one reference')
            ref = next(iter(selected)); c = changes[ref]
            props = [(x, y) for x, y in child_spans(block) if parse(block[x:y])[:2] == ['property', 'Value']]
            if len(props) != 1:
                raise ValueError('Missing/duplicate Value property: ' + ref)
            x, y = props[0]; prop = parse(block[x:y])
            if prop[2] != c['before']:
                raise ValueError('Value precondition does not match: ' + ref)
            tokens = [t for t in TOKEN.finditer(block[x:y]) if not t.group().isspace() and not t.group().startswith(';')]
            token = tokens[3]
            if not token.group().startswith('"'):
                raise ValueError('Value must be quoted')
            replacements.append((a + x + token.start(), a + x + token.end(), json.dumps(c['after'], ensure_ascii=False)))
            edits.append({'file': filename, 'ref': ref, 'unit': int(value(symbol, 'unit', 1)), **c})
            found.add(ref)
        for start, end, replacement in sorted(replacements, reverse=True):
            text = text[:start] + replacement + text[end:]
        parse(text)
        result[filename] = text.encode('utf-8')
    if found != set(changes):
        raise ValueError('Requested references not found: ' + ', '.join(sorted(set(changes) - found)))
    for filename in files.keys() - result.keys():
        result[filename] = (root.parent / filename).read_bytes()
    return result, audit, edits


def apply(root, contract, out, executable=None):
    root, out = Path(root).resolve(), Path(out).resolve()
    if out.exists() or out == root.parent or root.parent in out.parents:
        raise ValueError('Candidate output must be a new directory outside source project')
    blobs, audit, edits = prepare(root, contract)
    cli = find_cli(executable)
    if not cli:
        raise ValueError('KiCad CLI required for native verification')
    # Recheck after preparation; never write the source project.
    if frozen_files(root, audit_project(root)) != contract['baseline_files']:
        raise ValueError('Baseline changed during preparation')
    out.mkdir(parents=True)
    project, evidence = out / 'project', out / 'evidence'
    project.mkdir(); evidence.mkdir()
    for name, raw in blobs.items():
        target = project / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    (out / 'value-patch.json').write_text(json.dumps(contract, indent=2) + '\n')
    commands = []
    def run(args):
        proc = subprocess.run([cli, *args], capture_output=True, text=True, timeout=90)
        commands.append({'command': [cli, *args], 'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr})
        if proc.returncode:
            raise ValueError('KiCad export failed: ' + proc.stderr)
    error, change, final_audit = None, None, None
    try:
        for name, path in [('before', root), ('after', project / root.name)]:
            run(['sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(evidence / (name + '.xml')), str(path)])
        change = verify_change(evidence / 'before.xml', evidence / 'after.xml', {
            'schema_version': 1, 'component_changes': {ref: {'value': c} for ref, c in contract['changes'].items()}})
        if change['status'] != 'PASS':
            raise ValueError('Native identity/connectivity changed beyond requested Values')
        run(['sch', 'export', 'pdf', '-o', str(evidence / 'candidate.pdf'), str(project / root.name)])
        run(['sch', 'erc', '--format', 'json', '-o', str(evidence / 'candidate-erc.json'), str(project / root.name)])
        final_audit = audit_project(project / root.name, pdf=evidence / 'candidate.pdf')
        if final_audit['status'] != 'PASS':
            raise ValueError('Candidate hierarchy/PDF audit failed')
        if frozen_files(root, audit_project(root)) != contract['baseline_files']:
            raise ValueError('Baseline changed during native verification')
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        error = str(exc)
    report = {'schema_version': 1, 'status': 'FAIL' if error else 'PATCH_VERIFIED',
              'scope': 'Only requested Values changed; native pin partitions/identity and hierarchy preserved. Electrical review and rendered visual inspection remain pending; ERC export is not an ERC pass.',
              'baseline_files': contract['baseline_files'], 'candidate_files': {k: digest(v) for k, v in blobs.items()},
              'edits': edits, 'native_change': change, 'hierarchy': final_audit,
              'error': error, 'commands': commands, 'visual_review': 'REVIEW_PENDING', 'electrical_review': 'REVIEW_PENDING'}
    (out / 'patch-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report
