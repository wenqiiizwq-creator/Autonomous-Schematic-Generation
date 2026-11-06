"""Nets that leave the design to another board, declared in the electrical intent.

``intent["boundary_nets"]`` lists ``{"net", "to", "contract"}``: the net, the board or
design on the other side, and the interface contract document (relative to the
artifact root) that has a table row for the net. Such a net is drawn with a global
label even when it appears on one page only; KiCad's ``single_global_label`` finding
for it is waived, and so is ``isolated_pin_label`` (the label meets one pin: the other
end is off the board). Every other ERC finding stands. Undeclared nets keep the rule.
Matrix R2 (2026-11-04): about 40 nets to the MCU board were each drawn as a local
label with a per-net justification.
"""
import re

KEY = 'boundary_nets'
FIELDS = ('net', 'to', 'contract')
LABEL_NAME = re.compile(r"'(.*)'\s*$")
# The two findings that only say a label has no partner on this board.
WAIVABLE = ('single_global_label', 'isolated_pin_label')


def declarations(intent):
    """{net: declaration}; raises ValueError on a malformed list, an unknown or repeated net."""
    ds = intent.get(KEY, [])
    if not isinstance(ds, list):
        raise ValueError(KEY + ' must be a list')
    nets = {n['name'] for n in intent.get('nets', [])} if isinstance(intent.get('nets'), list) else set(intent.get('nets') or {})
    found = {}
    for d in ds:
        if not isinstance(d, dict) or set(d) != set(FIELDS) or any(not isinstance(d[k], str) or not d[k].strip() for k in FIELDS):
            raise ValueError(KEY + ' entries are {net, to, contract}, all nonempty')
        if d['net'] not in nets:
            raise ValueError('boundary net %s is not a net of the design' % d['net'])
        if d['net'] in found:
            raise ValueError('boundary net %s declared twice' % d['net'])
        found[d['net']] = d
    return found


def label_names(violation):
    """The label names an ERC violation's items quote (the description wording is localized, the quotes are not)."""
    names = []
    for item in violation.get('items') or []:
        m = LABEL_NAME.search(str(item.get('description') or ''))
        names.append(m.group(1) if m else None)
    return names


def split_erc(violations, intent):
    """(kept, waived): a WAIVABLE finding is waived when every label it names is a declared boundary net."""
    declared = declarations(intent)
    kept, waived = [], []
    for v in violations:
        names = label_names(v)
        if v.get('type') in WAIVABLE and names and all(n in declared for n in names):
            waived.append({'type': v['type'], 'nets': names, 'to': sorted({declared[n]['to'] for n in names})})
        else:
            kept.append(v)
    return kept, waived


def in_contract(net, text):
    """Whether a Markdown table row of the contract names the net as a whole word."""
    word = re.compile(r'(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])' % re.escape(net))
    return any(line.lstrip().startswith('|') and word.search(line) for line in text.splitlines())


def audit_contracts(intent, resolve, error, verified=None):
    """Each declared boundary net has a row in its contract document, and the document exists.
    ``resolve(path)`` returns the file or None; ``error(code, item)`` records a finding; a ``verified`` set receives
    the nets whose contract row was found (Matrix R3 S25: only these may have one pin on the board)."""
    try:
        declared = declarations(intent)
    except ValueError as exc:
        error('boundary_schema', exc)
        return []
    texts = {}
    for net, d in declared.items():
        if d['contract'] not in texts:
            path = resolve(d['contract'])
            try:
                texts[d['contract']] = path.read_text(encoding='utf-8') if path else None
            except (OSError, UnicodeError):
                texts[d['contract']] = None
        text = texts[d['contract']]
        if text is None:
            error('boundary_contract_missing', '%s：接口合同 %s 不存在或读不出' % (net, d['contract']))
        elif not in_contract(net, text):
            error('boundary_net_not_in_contract', '%s：接口合同 %s 的表格里没有这个网络的行' % (net, d['contract']))
        elif verified is not None:
            verified.add(net)
    return sorted(declared)
