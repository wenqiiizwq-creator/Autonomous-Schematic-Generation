"""record/architecture.json：功能块、电压域和跨块流向（references/quick-design.md 的“架构师”）。"""


def text(value):
    return isinstance(value, str) and bool(value.strip())


def board_nets(data):
    """{net: {block ids}} of the nets the flows carry, and the set of domain ground nets."""
    nets = {}
    for flow in (data or {}).get('flows') or []:
        if isinstance(flow, dict):
            for net in flow.get('nets') or []:
                nets.setdefault(net, set()).update(b for b in (flow.get('from'), flow.get('to')) if b)
    grounds = {d['ground'] for d in (data or {}).get('domains') or [] if isinstance(d, dict) and text(d.get('ground'))}
    return nets, grounds
