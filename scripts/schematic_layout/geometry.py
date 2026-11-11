"""Pure-domain schematic geometry: real symbol and text-field bounding boxes.

KiCad's file-level API does not expose rendered extents, so the placement and
readability engines historically approximated every symbol with a single fixed
half-size. That ignores two things that actually cause overlap and off-sheet
defects on rendered sheets:

* a symbol's real body/pin extent (a 48-pin MCU is not the size of an 0402), and
* the **text fields** (Reference, Value, …) that KiCad draws *outside* the body.

This module models both with no KiCad dependency, so it is fully unit-testable
and shared by the layout generator (``tools/schematic.py``) and the readability
QA engine (``models/visual_qa.py``). All coordinates are millimetres in KiCad's
schematic space (x right, y down).
"""

# Adapted from kicad-mcp-pro, Copyright (c) 2026 Osman Aslan, MIT.
# License: references/upstream-licenses/kicad-mcp-pro.txt.
from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

# KiCad's default schematic text height (mm). Property fields and labels use it
# unless the symbol overrides the font size.
DEFAULT_FONT_MM = 1.27

# Bounds are conservative planning estimates, not an exact KiCad font model.

# Extra width a bold field draws relative to a normal one.
_BOLD_WIDTH_FACTOR = 1.12


@dataclass(frozen=True, slots=True)
class Box:
    """An axis-aligned bounding box in millimetres."""

    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @classmethod
    def from_center(cls, cx: float, cy: float, width: float, height: float) -> Box:
        half_w = abs(width) / 2.0
        half_h = abs(height) / 2.0
        return cls(cx - half_w, cy - half_h, cx + half_w, cy + half_h)

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def center(self) -> tuple[float, float]:
        return ((self.x_min + self.x_max) / 2.0, (self.y_min + self.y_max) / 2.0)

    @property
    def area(self) -> float:
        return max(0.0, self.width) * max(0.0, self.height)

    def expanded(self, margin_mm: float) -> Box:
        """Return a copy grown outward by ``margin_mm`` on every side."""
        return Box(
            self.x_min - margin_mm,
            self.y_min - margin_mm,
            self.x_max + margin_mm,
            self.y_max + margin_mm,
        )

    def contains_point(self, x: float, y: float) -> bool:
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max

    def overlaps(self, other: Box, *, gap_mm: float = 0.0) -> bool:
        """Whether two boxes overlap, treating a clearance ``gap_mm`` as solid.

        ``gap_mm`` > 0 reports boxes that merely sit closer than the clearance as
        overlapping, which is what readability checks want (touching text is
        unreadable even before it strictly intersects).
        """
        return not (
            self.x_max + gap_mm <= other.x_min
            or other.x_max + gap_mm <= self.x_min
            or self.y_max + gap_mm <= other.y_min
            or other.y_max + gap_mm <= self.y_min
        )

    def intersection_area(self, other: Box) -> float:
        dx = min(self.x_max, other.x_max) - max(self.x_min, other.x_min)
        dy = min(self.y_max, other.y_max) - max(self.y_min, other.y_min)
        if dx <= 0.0 or dy <= 0.0:
            return 0.0
        return dx * dy

    def inside(self, container: Box, *, margin_mm: float = 0.0) -> bool:
        """Whether this box fits entirely within ``container`` (minus a margin)."""
        return (
            self.x_min >= container.x_min + margin_mm
            and self.y_min >= container.y_min + margin_mm
            and self.x_max <= container.x_max - margin_mm
            and self.y_max <= container.y_max - margin_mm
        )


def union(boxes: Iterable[Box]) -> Box | None:
    """Return the smallest box covering every input box, or ``None`` if empty."""
    items = list(boxes)
    if not items:
        return None
    return Box(
        min(b.x_min for b in items),
        min(b.y_min for b in items),
        max(b.x_max for b in items),
        max(b.y_max for b in items),
    )


def text_extent(
    text: str, font_mm: float = DEFAULT_FONT_MM, *, bold: bool = False
) -> tuple[float, float]:
    """Return the ``(width, height)`` a horizontal text string renders to (mm).

    Multiline, wide glyphs and CJK receive additional space. Native text bounds
    still require rendering; no character-count estimate guarantees all fonts.
    """
    if not text:
        return (0.0, 0.0)
    # Conservative estimate, NOT native KiCad font metrics. Account for wide
    # glyphs, CJK and multiline values; visual review remains a separate gate.
    import unicodedata

    lines = text.split("\n")

    def advance(line: str) -> float:
        return sum(
            1.05 if c not in "MW@%" and (unicodedata.east_asian_width(c) not in "WF" or unicodedata.category(c)[0] == "P")
            else 1.3 if c in "MW@%" else 1.55      # a CJK ideograph is 1.47 wide, full-width punctuation 0.87
            for c in line
        )

    width = max(map(advance, lines)) * font_mm
    if bold:
        width *= _BOLD_WIDTH_FACTOR
    return (width, font_mm * (1 + 1.4 * (len(lines) - 1)))


_TALL = frozenset("/\\()[]{}|$")
# How far below the capitals' foot a glyph reaches, in font heights (underscore 0.09, slash and descenders 0.33,
# brackets 0.43 measured).
_DEPTH = {**dict.fromkeys("()[]{}|", 0.45), **dict.fromkeys("/\\$gjpqy,;", 0.35), "_": 0.1, "Q": 0.1}
# Ink beyond the nominal text line, in font heights (above, below): symbol field, text note, local net name.
INK_MARGIN = {"field": (0.15, 0.45), "note": (0.52, 0.42), "label": (0.48, 0.0)}


@dataclass(frozen=True, slots=True)
class TextField:
    """A placed text field (Reference/Value/label) with KiCad justify + rotation.

    ``justify`` is the KiCad token set: any of ``left``/``right``/``top``/
    ``bottom`` (a blank set means centred on both axes, KiCad's default). ``angle``
    is the field rotation in degrees (0 or 180 horizontal, 90 or 270 vertical).
    """

    text: str
    x: float
    y: float
    angle: float = 0.0
    font_mm: float = DEFAULT_FONT_MM
    bold: bool = False
    justify: frozenset[str] = field(default_factory=frozenset)
    ink: str = field(default="field", kw_only=True)

    def box(self) -> Box:
        w, h = text_extent(self.text, self.font_mm, bold=self.bold)
        just = self.justify
        # Horizontal anchoring: KiCad grows text away from a left/right justify.
        if "left" in just:
            x_min, x_max = self.x, self.x + w
        elif "right" in just:
            x_min, x_max = self.x - w, self.x
        else:
            x_min, x_max = self.x - w / 2.0, self.x + w / 2.0
        # Vertical anchoring: top/bottom justify, else centred on the baseline.
        if "top" in just:
            y_min, y_max = self.y, self.y + h
        elif "bottom" in just:
            y_min, y_max = self.y - h, self.y
        else:
            y_min, y_max = self.y - h / 2.0, self.y + h / 2.0
        # KiCad's ink reaches past the nominal line: a slash, bracket or descender on a field, and a note or a local
        # name sits above its anchor (measured on KiCad 10 SVG at 1.0 and 1.27 mm, 2026-11-11; INK_MARGIN).
        above, below = INK_MARGIN[self.ink]
        if self.ink == "field":      # a field is centred on its capitals: only these glyphs leave the line
            above = above if set(self.text) & _TALL else 0.0
            below = max((_DEPTH.get(c, 0.0) for c in self.text), default=0.0)
        elif self.ink == "label" and set(self.text) & _TALL:
            above += 0.14
        elif self.ink == "note" and round(self.angle) % 180 == 0:
            below = 0.25             # only a turned note reaches 0.4 past its line
        y_min, y_max = y_min - above * self.font_mm, y_max + below * self.font_mm
        # Apply anchoring in text-local axes BEFORE rotating to the sheet.
        # Positive KiCad text angles are counterclockwise (sheet y points down).
        a = math.radians(-self.angle)
        c, s = math.cos(a), math.sin(a)
        points = [
            (
                self.x + (x - self.x) * c - (y - self.y) * s,
                self.y + (x - self.x) * s + (y - self.y) * c,
            )
            for x in (x_min, x_max)
            for y in (y_min, y_max)
        ]
        return Box(
            min(x for x, y in points),
            min(y for x, y in points),
            max(x for x, y in points),
            max(y for x, y in points),
        )


def parse_justify(tokens: str | Iterable[str] | None) -> frozenset[str]:
    """Normalise a KiCad ``(justify …)`` token list into a frozenset.

    Accepts the raw inner string (``"left bottom"``) or an iterable. Mirroring
    (``mirror``) and unknown tokens are dropped — only positional anchors matter
    for a bounding box.
    """
    if tokens is None:
        return frozenset()
    raw: Iterable[str]
    raw = tokens.split() if isinstance(tokens, str) else tokens
    keep = {"left", "right", "top", "bottom"}
    return frozenset(token for token in raw if token in keep)


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])
