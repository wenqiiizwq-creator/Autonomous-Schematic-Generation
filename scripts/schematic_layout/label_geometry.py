"""Global-label planning bounds, narrowly calibrated on KiCad 10.0.6.

Native passive outlines at 1.0/1.27 mm, default stroke font, plain ASCII and
four declared angle/justify pairs have a short axis of 2*font plus 0.1524 mm
stroke. The 0.002 mm total margin covers exported coordinate precision.
Long-axis text metrics remain conservative estimates. Other styles retain the
legacy envelope and a coverage gap; their native shape is not certified.
"""
from dataclasses import dataclass
from .geometry import Box, text_extent, union

STYLES = {
    (0, frozenset({'right'})): (-1, 0),
    (180, frozenset({'left'})): (1, 0),
    (90, frozenset({'left'})): (0, -1),
    (270, frozenset({'right'})): (0, 1),
}
DIRECTION_STYLE = {direction: style for style, direction in STYLES.items()}
CAP_MM = 0.1524 / 2 + 0.002 / 2


@dataclass(frozen=True)
class LabelOutline:
    box: Box
    anchor: tuple
    outward: tuple
    gaps: tuple = ()
    tip_contact: bool = False

    def terminal_contact(self, a, b):
        """Only an anchored straight exit at the native connection boundary.

        Here outward describes the label body, so the attaching segment must
        leave opposite the body or perpendicular along its anchor edge.
        Net identity alone grants no waiver.
        """
        if (self.gaps and not self.tip_contact) or self.anchor not in (a, b):
            return False
        other = b if a == self.anchor else a
        dx, dy = self.outward
        vx, vy = other[0] - self.anchor[0], other[1] - self.anchor[1]
        if self.box.contains_point(*other):
            return False
        along = vx * dx + vy * dy
        across = vx * dy - vy * dx
        # Native passive labels attach to a straight wire at the middle of
        # their near edge. A perpendicular endpoint runs on that edge, not
        # through the text. Exact anchor, cardinal direction and an endpoint
        # beyond the box are required; traversals and nearby wires still hit.
        if not self.gaps and abs(along) <= 1e-9 and abs(across) > 1e-9:
            return True
        if along >= -CAP_MM or abs(across) > 1e-9:
            return False
        # Project the actual box/segment intersection onto the body axis.
        axis = 0 if dx else 1
        direction = dx or dy
        lo = max(min(a[axis], b[axis]), (self.box.x_min, self.box.y_min)[axis])
        hi = min(max(a[axis], b[axis]), (self.box.x_max, self.box.y_max)[axis])
        projected = sorted((direction * (lo - self.anchor[axis]),
                            direction * (hi - self.anchor[axis])))
        return (-CAP_MM - 1e-9 <= projected[0] <= projected[1] <= 1e-9)


def global_outline(text, at, outward, font=1.27, *, shape='passive', bold=False,
                   italic=False, face=None, size=None, thickness=None,
                   angle=None, justify=None):
    gaps = []
    if outward not in DIRECTION_STYLE:
        raise ValueError('Global label direction must be a cardinal unit vector')
    expected_angle, expected_justify = DIRECTION_STYLE[outward]
    if angle is not None and angle % 360 != expected_angle:
        gaps.append('angle')
    if justify is not None and frozenset(justify) != expected_justify:
        gaps.append('justify')
    if shape != 'passive': gaps.append('shape')
    if bold: gaps.append('bold')
    if italic: gaps.append('italic')
    if face not in (None, ''): gaps.append('font face')
    if thickness not in (None, 0): gaps.append('font thickness')
    if font not in (1.0, 1.27): gaps.append('font size')
    if size is not None and tuple(size) != (font, font): gaps.append('unequal font axes')
    if not text or any(not 32 <= ord(c) <= 126 for c in text) or any(c in text for c in '~{}^\\'):
        gaps.append('plain single-line ASCII')
    width, height = text_extent(text, font, bold=bold)
    scale = font / 1.27
    length = width + 3.0 * scale
    half = font + CAP_MM
    if gaps:
        # Union of the previous generate/recipes and scene envelope, including
        # the complete anchor. Unknown shape remains a planning estimate.
        length = max(length, width + 3.0)
        half = max(1.5, 1.5 * scale, height / 2) + CAP_MM
    length += CAP_MM
    x, y = at
    dx, dy = outward
    if dx:
        x0, x1 = (x - CAP_MM, x + length) if dx > 0 else (x - length, x + CAP_MM)
        box = Box(x0, y - half, x1, y + half)
    else:
        y0, y1 = (y - CAP_MM, y + length) if dy > 0 else (y - length, y + CAP_MM)
        box = Box(x - half, y0, x + half, y1)
    if 'angle' in gaps or 'justify' in gaps:
        box = union([box, Box(x - length, y - half, x + length, y + half),
                          Box(x - half, y - length, x + half, y + length)])
    # Default-font input arrow tips have the same native stroke contact at
    # the anchor. This certifies a collinear exit only, not the uncalibrated
    # arrow outline. KiCad's exact {slash} escape does not change tip contact;
    # all other untested text/font/style properties retain the gap and block it.
    decoded = text.replace('{slash}', '/')
    tip_contact = (shape in ('passive', 'input')
                   and not (set(gaps) - {'shape', 'plain single-line ASCII'})
                   and bool(decoded)
                   and all(32 <= ord(c) <= 126 for c in decoded)
                   and not any(c in decoded for c in '~{}^\\'))
    return LabelOutline(box, tuple(at), outward, tuple(gaps), tip_contact)
