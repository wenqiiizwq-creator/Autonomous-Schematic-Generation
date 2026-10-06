# Drawing recipes (readable sheets from pin geometry)

Use for every sheet a person will read, new or redrawn. The agent writes a short
page script that states **structure**; `schematic_layout.recipes.Sheet` derives
the geometry from the real library pins and writes explicit wires. This is the
construction layer behind [human-readable-routing.md](human-readable-routing.md).

Readable wiring is a placement problem. When a pin faces away from the net it
joins, every router has to loop back. On a 100 W charger the hand-placed v0.2.2
pages had 29 different-net crossings and 237 bends. The same circuit, redrawn by
placing support parts from their pins with explicit spines, had 0 crossings and
82 bends.

## Workflow

1. Write the presentation plan (reading path, blocks, rails, labels) per
   human-readable-routing.md section 1.
2. `sheet = Sheet(intent, rails={...}, external=[...])` and read `sheet.plan`:
   the proposed role of every part and the label role of every net.
3. Write the page script following the outline rules below: place anchors,
   then draw every other part with the recipe its role allows. Keep coordinates
   only for anchors and deliberate Z legs. Record each intended deviation with
   `sheet.justify(part_or_net, reason)` where it is made.
4. `root, report = sheet.build(name)`, then write `dump(root)`. Build raises on
   any hard defect (see below); fix the structure, not the symptom.
5. `report["structure"]` must be PASS: every finding is either fixed or a
   recorded deviation with its reason.
6. Native checks: netlist partition identity (`compare_netlist(xml, intent,
   report["layout"])`), ERC, `check_schematic_geometry.py`, symbol integrity.
7. Mandatory: `scripts/check_schematic_readability.py` on the written sheet.
8. Render natively and trace each declared reading task.

## Outline rules (how to decide the structure)

The agent owns the topology decisions; these rules make them repeatable. Apply
them in order; later rules never override earlier ones.

| # | Decision | Rule |
| --- | --- | --- |
| O1 | Page flow | The main energy/signal path runs left to right along one row, from the input interface to the output interface. A second path gets its own row below; rows are ordered by the path's position in the system. |
| O2 | Anchors | Anchors are parts with three or more pins and connectors. One block per anchor; place anchors first, on the main row in path order, upright. Rotate or mirror only when the pin sides otherwise invert the flow (inputs should face upstream). |
| O3 | Ownership | A two-pin part belongs to the anchor whose pin net it touches; a part between two anchors belongs to the path between them and is drawn in path order. Never draw a support part inside another anchor's block. |
| O4 | Recipe by role | Use the proposed role from `sheet.plan`: `series` on the path axis; `shunt` off its node toward its rail (returns down, supplies up); `bank` for parallel parts on the same nets, as one bank with one return; `divider` stacked with the tap sideways to the sense pin; `lane_*` as identical series+shunt lanes with the same arrangement; `decoupling` as a shunt or bank at its anchor's supply pin. |
| O5 | Pin exits | Start each branch from the pin along its outward direction (`stub`, or a recipe started at the pin). A support branch that must reach a pin on the far side of its anchor goes over or under the anchor block, never through another branch; if that is impossible, move the part to that pin's side. |
| O6 | Rails and labels | Rails and returns are power symbols from the declared `rails`; global labels only on `external` nets; small names on the plan's `name` nets; a local join label only with a boundary reason. |
| O7 | Spacing | Recipe gaps are at least two grid steps; widen a gap before moving parts by hand. A net that carries a small name needs one straight run longer than the name plus two grid steps. A vertical part with a long value needs that text width free on one side. Pins 7.62 mm apart cannot both hang a shunt down: fold one branch up or make the lower pin's run shorter than the upper one's. Blocks are separated by more space than parts inside a block. |
| O8 | Repair order | On a build error or failing gate, first change the recipe direction, gap or order; then the anchor position; then split the block into rows. Never add a label to hide a failed wire. |

The audit checks what can be checked from the drawing: the recipe used for
each part against its role, banks drawn as one bank, repeated lanes with an
identical arrangement, global labels exactly on external nets, rails drawn only
with their power symbols, selected names present and no unselected local label
without a reason. O1, O2, O3 and O5 remain review items: trace them in the render.

## API

| Call | Draws |
| --- | --- |
| `Sheet(intent, rails, external, paper, dirs, power_ref_start)` | One sheet. `rails` maps nets to `power:` symbols, `external` lists nets leaving the sheet; both enable `plan` and the audit. `power_ref_start` keeps `#PWR` references unique across pages. |
| `plan` | `{"parts": {ref: {role, why, ...}}, "nets": {net: "power" \| "global" \| "name" \| None}}`. |
| `justify(part_or_net, reason)` | Records an intended deviation; the audit lists it with the reason. |
| `place(ref, at, rotation, mirror)` | An anchor: controller, connector, magnetic, bridge. |
| `put(ref, pin, at, toward)` | Part with `pin` on `at`, extending along `toward` (pin faces back). Parts with more than two pins stay upright. |
| `stub(pin, n)` | Pin exit along its own direction; returns the end point. |
| `series(start, [refs], toward, gap, net)` | Series chain on one axis in circuit order; the pin on the current net faces the start. Returns far-pin points. |
| `shunt(node, ref, toward, gap, rail)` | Two-pin branch off a node; far pin gets its declared rail symbol (`rail=False`: the far pin is returned). |
| `bank(start, refs, toward, hang, pitch, gap, rail, common, depth, lead)` | Parallel parts off a spine at a measured pitch; with `common` one straight return line and one symbol (`rail=False`: the common line is a signal net, e.g. N_EMI under L_EMI, or a gate line beside a drive line). `depth` fixes the common line's distance; `lead=0` puts the first part at `start` (inline with a pin). `hang=RIGHT` with `toward=DOWN` gives the classic side-by-side parallel pair. Returns the spine end. |
| `divider(top, upper, lower, toward, gap, rail)` | Stacked divider; returns the tap point on the midpoint wire. |
| `connect(a, b, first, x, y)` | L (`first` h/v) or Z (middle leg at `x` or `y`) between pins/points. |
| `wire(*pins_or_points, net)` | Explicit orthogonal polyline; every pin must be on `net`. |
| `power(target, symbol, net, length)` | Rail/return symbol whose Value is the net name (declared symbol by default); a perpendicular pin is left sideways far enough to clear the part body. |
| `label(target, kind, length, outward, net, reason)` | Global label where the net leaves the sheet, or a local join with `reason`. Extends along the pin direction or `outward`: left, right, up or down. |
| `name(net, at)` | Small 1.0 mm local name on the net's own wire, mid-segment and clear of pins and dots: above a horizontal wire, else beside a vertical one. |
| `select_local_names(intent, external, rails)` | Default selection: page-local nets touching a part with three or more pins. |
| `text(text, at, font)` | Block title or note. |

`build(name, draft=False)` returns the native root and a report. With `draft=True`
name and field failures are listed in `draft_failures` instead of raised, so a
page can be rendered while it is being fixed; a draft is never delivered. Fields
that fit on no side (bridges, parts wired on all four sides) take a clear body
corner. Content stays 12 mm inside the drawing-sheet frame. The report holds every recipe decision, crossing
locations, label and rail sets, readability metrics with the gate, the
structure audit, and a `layout` whose net policies `compare_netlist` uses to
check label and rail names.

For a multi-page project, build each page with its own `power_ref_start`, then
restore the baseline identity (symbol properties, UUIDs, pin UUIDs, instance
paths, page UUID, title block) before writing. The charger redraw
(`design/v0.2.5-recipes/scripts/redraw.py` in that project) is a worked example
of nine hierarchical pages drawn this way.

Native label styles (render-verified on KiCad 10.0.6): global labels extend
left at 0/`right`, right at 180/`left`, up at 90/`left`, down at 270/`right`;
local labels use 0/`left bottom`, 180/`right bottom`, 90/`left bottom`,
270/`right bottom`, and KiCad draws their text readable (above a horizontal
wire, left of a vertical one).

## Hard rejections in `build()`

- Unplaced parts; off-grid or coincident terminals (from `make_root`).
- Diagonal wires; a wire over another net's terminal; different nets touching
  or overlapping (a clean perpendicular crossing is allowed but reported).
- A wire through a part body (bodies cut back at their own pin tips), leaving the
  drawing area or entering the title block.
- An unwired pin; a net drawn in separate pieces unless every piece carries its
  label or rail symbol.
- A rail symbol, label or name that collides; no clear Reference/Value position.

Typical fixes: lengthen a `gap` or stub, change a recipe direction, move an
anchor, split a crowded block into rows, reverse a chain's order. Never replace
a failed wire with a label unless the plan declares that boundary.

## Worked example

`tests/fixtures/drawing/recipe_board.py` draws a 12 V to 5 V buck, a 3.3 V LDO
with indicator, and two USB ESD lanes on A4 (22 parts, 0 crossings, 11 bends):

```python
s = Sheet(INTENT, rails={'GND': 'power:GND', '+5V': 'power:+5V', '+3V3': 'power:+3V3'},
          external=['MCU_DP', 'MCU_DN', 'USB_VBUS'])
s.place('J1', (20.32, 50.8)); s.power('J1.2')
s.series('J1.1', ['F1', 'D1'], RIGHT, gap=3)            # input chain
vin = s.bank('D1.1', ['C1', 'C2'], RIGHT)               # input bank, one return
s.put('U1', '1', add(vin, RIGHT, 12), RIGHT); s.wire(vin, 'U1.1')
sw = s.stub('U1.2', 3); s.shunt(sw, 'D2', DOWN)          # catch diode at SW
out = s.bank(s.series(sw, ['L1'], RIGHT, gap=6)[-1], ['C3', 'C4'], RIGHT)
rail = s.wire(out, add(out, RIGHT, 3)); s.power(rail)   # declared +5V symbol
r1 = s.series(rail, ['R1'], RIGHT, gap=3)[-1]            # upper divider leg
tap = s.wire(r1, add(r1, RIGHT, 2)); s.shunt(tap, 'R2', DOWN)
fb = s.stub('U1.4', 2); s.connect(fb, tap, y=fb[1] - 10.16)   # FB over the top
```

`draw(bad=True)` is the negative example: the same netlist with the feedback
wire dropped through the +5 V spine and the LED reversed into a U-turn. The gate
names the crossing (`+5V`/`FB`) and the tortuous connection (`D3.2`, `R3.2`);
the structure audit names D3, placed by hand although its role is a shunt.

## Keep the generator with the delivery

Store the page scripts (intent derivation, recipe redraw, assembly) inside every delivered
revision directory, next to the native project. The next electrical revision regenerates only
its changed pages from the previous revision's intent plus these scripts; a delivery without its
generator forces hand edits of readable pages, which this workflow forbids. Directory clean-ups
must not delete a revision's generator while a later revision still derives from it.

## Limits

- The agent chooses structure; nothing here recognizes a topology.
- Single-unit symbols only. A functional pin-grouped presentation symbol needs
  its own verified physical pin map (see symbol-and-peripheral-contracts.md).
- One `Sheet` per page. For a hierarchical project, copy each symbol's project
  instance path and UUID from the baseline page, as a redraw must preserve them.
- `check_scene` accepts a pin's own straight outward exit through graphics
  that reach past its tip (LED arrows, magnetics arcs, thermistor marks); any
  other wire through the body box is still reported.
- Text widths are estimates; native render review remains mandatory.
