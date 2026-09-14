"""Small typed S-expression reader/writer; quoted values stay quoted.

Used only by the generation/geometry modules. Existing analysis parsers are
unchanged. Parsing never evaluates input and rejects trailing/truncated input.
"""

import re
import json


class Atom(str):
    pass


def parse(text):
    pattern = re.compile(r'\s+|;[^\n]*|\(|\)|"(?:\\.|[^"\\])*"|[^\s();"]+')
    tokens, end = [], 0
    for match in pattern.finditer(text):
        if match.start() != end:
            raise ValueError(f"Invalid S-expression at character {end}")
        end = match.end()
        token = match.group()
        if not token.isspace() and not token.startswith(";"):
            tokens.append(token)
    if text[end:].strip():
        raise ValueError("Unterminated S-expression string")
    stack, root = [], None
    for token in tokens:
        if token == "(":
            node = []
            if stack:
                stack[-1].append(node)
            elif root is not None:
                raise ValueError("Multiple S-expression roots")
            else:
                root = node
            stack.append(node)
        elif token == ")":
            if not stack:
                raise ValueError("Unexpected closing parenthesis")
            stack.pop()
        else:
            if not stack:
                raise ValueError("Atom outside root")
            if token.startswith('"'):
                # KiCad only escapes quote/backslash/newline; preserve other
                # backslash pairs instead of interpreting arbitrary escapes.
                value = re.sub(
                    r'\\([\\"nr])',
                    lambda m: {"n": "\n", "r": "\r"}.get(m[1], m[1]),
                    token[1:-1],
                )
            else:
                value = Atom(token)
            stack[-1].append(value)
    if stack or root is None:
        raise ValueError("Incomplete S-expression")
    return root


def dump(node):
    if isinstance(node, list):
        return "(" + " ".join(map(dump, node)) + ")"
    if isinstance(node, Atom):
        return str(node)
    if isinstance(node, (int, float)):
        return format(node, ".10g")
    return json.dumps(str(node), ensure_ascii=False)


def all_nodes(node, key):
    return [n for n in node if isinstance(n, list) and n and n[0] == key]


def first(node, key, default=None):
    return next(iter(all_nodes(node, key)), default)


def value(node, key, default=None):
    n = first(node, key)
    return n[1] if n and len(n) > 1 else default


def form(key, *items):
    return [Atom(key), *items]


def set_node(node, key, *items):
    old = first(node, key)
    if old is not None:
        node[node.index(old)] = form(key, *items)
    else:
        node.append(form(key, *items))
