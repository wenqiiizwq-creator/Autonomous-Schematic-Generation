"""record/architecture.json：任务 C2.1（模块 C2）的系统架构与块规格（references/modules.md）。"""

FLOW_KINDS = ('power', 'signal')


def text(value):
    return isinstance(value, str) and bool(value.strip())


def check_architecture(data, requirement_ids=None):
    """record/architecture.json (task C2.1, module C2): each block has inputs, outputs, a voltage domain, a block
    specification and its own reference-number range; each cross-block flow is named, joins two blocks and names the
    board nets it carries and their interface parameters; each isolation boundary names domains that hold
    blocks on both sides. Returns the problems."""
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        return ['architecture.json 要写 schema_version 1（见 references/modules.md）']
    problems = []
    domains = data.get('domains')
    if not isinstance(domains, list) or not domains or any(not isinstance(d, dict) or not text(d.get('name')) for d in domains):
        problems.append('architecture.json 要列 domains：每个电压域写 name')
        domains = []
    domain_names = [d['name'] for d in domains if isinstance(d, dict) and text(d.get('name'))]
    for d in domains:
        if isinstance(d, dict) and 'ground' in d and not text(d.get('ground')):
            problems.append('architecture.json 电压域 %s 的 ground 要写这个域的地网络名' % d.get('name'))
    if len(set(domain_names)) != len(domain_names):
        problems.append('architecture.json 的电压域名重复')
    blocks = data.get('blocks')
    if not isinstance(blocks, list) or not blocks:
        return problems + ['architecture.json 要列 blocks：每个功能块写 id、name、domain、inputs、outputs、spec']
    ids, by_domain, ranges = set(), {}, []
    for i, block in enumerate(blocks, 1):
        if not isinstance(block, dict) or not text(block.get('id')):
            problems.append('architecture.json 第 %d 个功能块要写 id' % i)
            continue
        where = 'architecture.json 功能块 %s' % block['id']
        if block['id'] in ids:
            problems.append(where + ' 的 id 重复')
        ids.add(block['id'])
        if not text(block.get('name')):
            problems.append(where + ' 要写 name')
        if block.get('domain') not in domain_names:
            problems.append(where + ' 的 domain 要是 domains 里的一个电压域')
        else:
            by_domain.setdefault(block['domain'], []).append(block['id'])
        for field in ('inputs', 'outputs'):
            values = block.get(field)
            if not isinstance(values, list) or not values or not all(text(v) for v in values):
                problems.append('%s 要写 %s（非空的名称列表）' % (where, field))
        span = block.get('ref_range')
        if not (isinstance(span, list) and len(span) == 2 and all(isinstance(n, int) and not isinstance(n, bool) and n >= 0
                                                                  for n in span) and span[0] <= span[1]):
            problems.append(where + ' 要写位号编号段 ref_range：[起, 止]，本块器件位号的数字部分在段内')
        else:
            ranges.append((span[0], span[1], block['id']))
        spec = block.get('spec')
        if not isinstance(spec, dict) or not text(spec.get('text')):
            problems.append(where + ' 要写块规格 spec.text：输入、输出、功率与指标，只写要什么，不写拓扑')
        elif requirement_ids is not None:
            refs = spec.get('requirements', [])
            if not isinstance(refs, list) or any(r not in requirement_ids for r in refs):
                problems.append(where + ' 的 spec.requirements 要是 requirements.json 里的需求编号')
    ranges.sort()
    for (lo, hi, a), (lo2, _, b) in zip(ranges, ranges[1:]):
        if lo2 <= hi:
            problems.append('architecture.json 功能块 %s 与 %s 的位号编号段重叠' % (a, b))
    flows = data.get('flows')
    if not isinstance(flows, list):
        problems.append('architecture.json 要列 flows（跨块流向，没有时写空列表）')
        flows = []
    names = set()
    for i, flow in enumerate(flows, 1):
        if not isinstance(flow, dict) or not text(flow.get('name')):
            problems.append('architecture.json 第 %d 条跨块流向要写 name（它代表的电源轨或信号）' % i)
            continue
        where = 'architecture.json 流向 %s' % flow['name']
        if flow['name'] in names:
            problems.append(where + ' 重名')
        names.add(flow['name'])
        if flow.get('kind') not in FLOW_KINDS:
            problems.append(where + ' 的 kind 要是 %s' % '/'.join(FLOW_KINDS))
        if flow.get('from') not in ids or flow.get('to') not in ids or flow.get('from') == flow.get('to'):
            problems.append(where + ' 的 from、to 要是两个不同功能块的 id')
        nets = flow.get('nets')
        if not isinstance(nets, list) or not nets or not all(text(n) for n in nets):
            problems.append(where + ' 要写 nets：它承载的整板网络名')
        params = flow.get('params')
        if not ((isinstance(params, dict) and params) or text(params)):
            problems.append(where + ' 要写接口参数 params（电源轨写电压范围与最大电流，信号写电平、方向与驱动方式，'
                            '模拟量写量程与源阻抗，差分对写差分阻抗）')
    boundaries = data.get('boundaries')
    if not isinstance(boundaries, list):
        problems.append('architecture.json 要列 boundaries（隔离边界，没有时写空列表）')
        boundaries = []
    for i, boundary in enumerate(boundaries, 1):
        sides = boundary.get('sides') if isinstance(boundary, dict) else None
        where = 'architecture.json 第 %d 条隔离边界' % i
        if not isinstance(sides, list) or len(sides) < 2 or any(s not in domain_names for s in sides):
            problems.append(where + ' 的 sides 要列至少两个电压域')
            continue
        empty = [s for s in sides if not by_domain.get(s)]
        if empty:
            problems.append('%s 的 %s 一侧还没有功能块' % (where, '、'.join(empty)))
    interfaces = data.get('interfaces', [])
    if not isinstance(interfaces, list) or any(not isinstance(x, dict) or not text(x.get('name')) or x.get('block') not in ids
                                               for x in interfaces):
        problems.append('architecture.json 的 interfaces 每项写 name 和所属功能块 block')
    return problems


def board_nets(data):
    """{net: {block ids}} of the nets the flows carry, and the set of domain ground nets."""
    nets = {}
    for flow in (data or {}).get('flows') or []:
        if isinstance(flow, dict):
            for net in flow.get('nets') or []:
                nets.setdefault(net, set()).update(b for b in (flow.get('from'), flow.get('to')) if b)
    grounds = {d['ground'] for d in (data or {}).get('domains') or [] if isinstance(d, dict) and text(d.get('ground'))}
    return nets, grounds
