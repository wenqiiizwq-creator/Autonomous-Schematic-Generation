"""Split one board electrical intent into per-page drawing intents.

A board intent lists every component once, with the page it is drawn on in a
field (``fields.Circuit`` by default), its nets as ``{name: [pins]}`` or as a
list of ``{"name", "pins"}`` and its intentional ``no_connect`` pins. Each page
intent keeps the page's components unchanged (value, MPN, datasheet, fields),
the page-local part of every net, and the page's NC pins. A net is external to a
page when it also has pins on another page and is not a declared rail; these
are the nets that need a global label (outline rule O6).
"""

import copy


def board_nets(board):
    """Nets as a list of ``{"name", "pins"}`` from either supported form."""
    nets = board["nets"]
    if isinstance(nets, dict):
        return [{"name": name, "pins": list(pins)} for name, pins in nets.items()]
    return [{"name": n["name"], "pins": list(n["pins"])} for n in nets]


def normalize(board):
    """The board as a generator intent (schema_version 1, list nets), for native comparison."""
    intent = {k: copy.deepcopy(v) for k, v in board.items() if k not in ("schema", "nets")}
    intent["schema_version"] = 1
    intent["nets"] = board_nets(board)
    intent.setdefault("no_connect", [])
    return intent


def page_intents(board, field="Circuit", page_of=None, rails=()):
    """``{page: {"intent", "external", "rails"}}`` in first-appearance page order.

    ``page_of`` maps reference to page and overrides ``fields[field]``. Every
    component must have a page and every pin must belong to a known component.
    ``rails`` (names, or ``{net: "power:..."}``) is returned per page restricted
    to the nets on that page, ready for ``Sheet(intent, rails=..., external=...)``.
    """
    components = board["components"]
    refs = {c["ref"] for c in components}
    pages = {}
    for c in components:
        page = (page_of or {}).get(c["ref"]) or c.get("fields", {}).get(field)
        if not page:
            raise ValueError(f"{c['ref']} has no page; set fields.{field} or page_of")
        pages[c["ref"]] = page
    nets = board_nets(board)
    for pid in [p for n in nets for p in n["pins"]] + list(board.get("no_connect", [])):
        if pid.rsplit(".", 1)[0] not in refs:
            raise ValueError(f"Pin {pid} belongs to no component")
    symbols = dict(rails) if isinstance(rails, dict) else None
    rails = set(rails)
    result = {}
    for page in dict.fromkeys(pages[c["ref"]] for c in components):
        local = [n for n in nets if any(pages[p.rsplit(".", 1)[0]] == page for p in n["pins"])]
        intent = {
            "schema_version": 1,
            "title": page,
            "revision": board.get("revision", "draft"),
            "design_id": f"{board.get('design_id', 'board')}-{page}",
            "components": [copy.deepcopy(c) for c in components if pages[c["ref"]] == page],
            "nets": [{"name": n["name"], "pins": [p for p in n["pins"] if pages[p.rsplit(".", 1)[0]] == page]}
                     for n in local],
            "no_connect": [p for p in board.get("no_connect", []) if pages[p.rsplit(".", 1)[0]] == page],
        }
        supplies = [copy.deepcopy(d) for d in board.get("external_supply", [])
                    if pages.get(str(d.get("pin", "")).rsplit(".", 1)[0]) == page]
        if supplies:  # The flag goes on the page of the declared connector pin.
            intent["external_supply"] = supplies
        external = sorted(n["name"] for n in local if n["name"] not in rails
                          and any(pages[p.rsplit(".", 1)[0]] != page for p in n["pins"]))
        names = {n["name"] for n in local}
        page_rails = ({n: s for n, s in symbols.items() if n in names} if symbols is not None
                      else sorted(rails & names))
        result[page] = {"intent": intent, "external": external, "rails": page_rails}
    return result
