"""Optional electrical roles, independent of a net name or drawing glyph."""


def validate_net_roles(intent, power_nets=()):
    roles = intent.get('net_roles', {})
    if not isinstance(roles, dict):
        raise ValueError('net_roles must map net names to power, return, or signal')
    nets = intent['nets']
    names = set(nets) if isinstance(nets, dict) else {n['name'] for n in nets}
    for net, role in roles.items():
        if net not in names or role not in ('power', 'return', 'signal'):
            raise ValueError(f'Invalid net_roles declaration: {net!r}={role!r}')
    conflicts = sorted(net for net in power_nets if roles.get(net) == 'signal')
    if conflicts:
        raise ValueError(f'Signal nets cannot use power symbols: {conflicts}; use local/global labels, or, when the net '
                         'feeds a part (an external_supply, filtered_supply or reviewed_circuit_supply net carries a '
                         'PWR_FLAG), declare it power in net_roles')
    return roles
