# Deterministic single-sheet generation

Read this when turning an established circuit into a new native KiCad drawing.
For modular circuit input and automatic placement use [Circuit IR v2](circuit-ir.md).
This lower-level interface accepts a reviewed circuit and explicit placement; the scripts
resolve real symbol geometry, place visible fields, route wires and verify.
They do not select ICs, infer missing connections, or optimize arbitrary boards.

## Supported scope

- Python 3.10+ standard library only at runtime; installed native KiCad CLI and
  official/custom symbol libraries. Execution tested on KiCad **10.0.4**.
- A single landscape ISO A sheet with real cached
  symbols, rectangles/polylines/circles/arcs, orthogonal rotation and x/y mirror.
  Symbol inheritance is resolved from the selected `.kicad_sym` library.
  Multi-unit components require an explicit complete `units` list (e.g. `[1,2,3]`)
  and placements keyed `U1:1`, `U1:2`, `U1:3`. Physical net pins remain `U1.number`.
- Separate physical pin IDs `reference.number` and named electrical nets.
  Every real pin must appear exactly once in a net or `no_connect`.
- Explicit placements, optional horizontal rails, visible local wires, and
  intentionally remote local labels. The router rejects different-net crossings
  rather than trying to route a general nonplanar schematic.
- Same-symbol coincident terminals on one connected net, including supported
  hidden passive copies, retain separate physical pin numbers in native export.
  Conflicting assignments and unsupported hidden/stacked arrangements fail.
- Full hierarchical authoring, unsupported stacked/hidden pins,
  power/virtual symbols without normal native netlist component
  identity, graphical bus authoring and arbitrary in-place edits need another writer.
  Do not alter a real symbol merely to force it through this bounded backend.
  Existing hierarchical projects use the staged, project-specific workflow in
  [existing-project-redraw.md](existing-project-redraw.md), not the single-sheet
  CLI as an automatic hierarchy editor.

## Inputs: intent and layout stay separate

The runnable examples are
`tests/fixtures/generation/rc_filter.intent.json` and
`tests/fixtures/generation/rc_filter.layout.json`. Their values are test fixtures,
not a qualified hardware design. Use a new output directory for each run.

`electrical_intent.json`:

```json
{
  "schema_version": 1,
  "title": "Reviewed circuit block",
  "revision": "draft",
  "components": [
    {"ref":"R1","lib_id":"Device:R","value":"10k","footprint":"Resistor_SMD:R_0603_1608Metric","mpn":"actual selected part","datasheet":"source URL"},
    {"ref":"R2","lib_id":"Device:R","value":"10k","footprint":"Resistor_SMD:R_0603_1608Metric"}
  ],
  "nets": [{"name":"DIV_MID","pins":["R1.2","R2.1"]}],
  "no_connect": ["R1.1","R2.2"]
}
```

This syntax example is only two interconnected test resistors, not an actual
divider design. For a real circuit include all required rails and components.
Optional component `dnp` is preserved in the schematic. Datasheet equations,
ratings and engineering decisions belong in accompanying design evidence; the
generator does not convert a supplied URL or value into electrical verification.

`layout_plan.json`:

```json
{
  "schema_version": 1,
  "paper": "A4",
  "grid_mm": 1.27,
  "placements": {
    "R1":{"at":[50.8,50.8],"rotation":0},
    "R2":{"at":[50.8,76.2],"rotation":0}
  },
  "nets": {"DIV_MID":{"label":true}}
}
```

Coordinates are millimetres, X right/Y down. Each component gets `at`, optional
`rotation` (0/90/180/270), optional `mirror` (`x` or `y`). Placement entries must
cover exactly the component references. Do not use library-local pin coordinates
as sheet coordinates: the backend rotates, mirrors and flips the Y axis, then
checks the resulting pin tips against the chosen grid without snapping them.
Unknown layout/placement/routing keys are rejected to expose spelling mistakes.
Hidden `fields`/`ratings`, MPN, Datasheet and DNP are preserved and compared in
native XML; multi-unit pin coverage is checked too. Optional `design_id` and
component `stable_id` bind UUIDs to stable identity instead of changing values.
Native fields are written with centred anchors to avoid mirror-dependent side
justification; local labels use the verified horizontal 0-degree style.

Per-net layout options:

| Key | Meaning |
| --- | --- |
| `mode: "wire"` | Default. MST pairing + bounded orthogonal routing; failure stays failure. |
| `mode: "labels"` | Intentional remote connection. Every pin receives a checked outward stub and the same local label. Crowded labels can fail. |
| `rail_y: number` | Fixed horizontal rail; attach this net's pins to the rail. Only in wire mode. |
| `label: true` | Add one visible net label on a successfully routed wire. |
| `priority: number` | Lower routes first. One reversed net-order retry is permitted. |

Optional `reserved` is a list of `[xmin,ymin,xmax,ymax]` keepouts. The default
reserves the lower-right 115×40 mm region with a 5 mm sheet margin. For a custom
drawing sheet, explicitly map its actual title/notes keepouts and verify its
native rendering. Optional `max_route_states` defaults to 150000 per pair.
Check the actual native printing frame as well as this backend's keepout; a
5 mm model margin does not establish clearance from a 10 mm native frame.
Prefer the native 1.27 mm connection grid. A finer geometry grid (e.g. 0.635 mm)
alone does not suppress native off-grid findings. Check the transformed pin
tips against native ERC; never silently shift electrical pins to make a check pass.

## Commands and outputs

Run from the skill/repository root; substitute its absolute path elsewhere:

```bash
python3 scripts/generate_schematic.py \
  tests/fixtures/generation/rc_filter.intent.json \
  tests/fixtures/generation/rc_filter.layout.json \
  --output-dir output/rc-filter-run-01 --name rc_filter

python3 scripts/check_schematic_geometry.py \
  output/rc-filter-run-01/rc_filter.kicad_sch \
  --intent output/rc-filter-run-01/electrical_intent.json \
  --layout output/rc-filter-run-01/layout_plan.json \
  --output output/rc-filter-run-01/geometry-recheck.json

python3 scripts/analyze_schematic.py \
  output/rc-filter-run-01/rc_filter.kicad_sch \
  --output output/rc-filter-run-01/analysis.json
```

Use `--symbol-dir /path/to/symbols` (repeatable) or `--kicad-cli /path/to/kicad-cli`
when auto-discovery is insufficient. The new output project gets a local
`sym-lib-table` bound to the actual libraries read; global KiCad configuration
is untouched. Those absolute library paths need rebinding on another machine.

- Copied intent/layout inputs allow reproducing failures.
- `generation.json` records input/library hashes, resolved pins/fields, routing
  order/retries, wire/junction counts and geometry findings.
- `.kicad_sch`, `.kicad_pro`, `sym-lib-table` form the native editable project.
- `native/erc.json`, `native/netlist.xml`, `native/schematic.pdf` are KiCad outputs.
- `native/symbol-integrity.json` checks actual pin-to-body strokes and physical
  pin coverage. It is a required native verification gate, including custom symbols.
- Optional `--reference-contract path/to/contract.json` adds source/pin/peripheral
  facts as a required gate and writes `native/reference-contract.json`. Schema,
  coverage and limits: [symbol-and-peripheral-contracts.md](symbol-and-peripheral-contracts.md).
- `verification.json` records exact schematic SHA-256, CLI version/commands and
  gate results. Routing/schema failures preserve the original input files and
  an error report; an existing output directory is never overwritten.

Exit 0 / `AUTOMATED_PASS` means geometry within its declared model, symbol
integrity, native ERC, exact netlist partitions and any supplied reference
contract passed, and a PDF was produced. It is **not final
design acceptance**. `native_render_review` and `datasheet_review` remain
`PENDING` until a separate evidence-backed review is performed.

## Geometry coverage and review

The checker reads the serialized native file independently. It checks body
clearance, wires through bodies, Reference/Value/labels including same-owner
collisions, text versus pin legs/wires, page/title keepouts, off-grid electrical
anchors, floating labels/NC markers/junctions, orphan endpoints, duplicate wires,
undotted crossings and cross-net contact when pin intent is supplied.

`PASS` means no finding within the model. `FAIL` is a detected defect;
`INSUFFICIENT` is unsupported geometry or missing cached symbols; `REVIEW` is a
remaining warning such as an undotted crossing. Never erase the coverage gaps
to force a passing report. Pin names/numbers, custom drawings and exact font
metrics require native rendering. Arc bounds are conservative full-circle boxes.
Existing rotated/mirrored non-centred fields and other local-label spins are
reported as coverage gaps, because their native alignment is not modeled here.
Legal shared electrical nodes and wire corners do not require decorative dots.

Render the native PDF to PNG and inspect both the full page and occupied regions:

```bash
pdftoppm -scale-to 2200 -png -singlefile \
  output/rc-filter-run-01/native/schematic.pdf \
  output/rc-filter-run-01/native/schematic
```

Review electrical calculations and analyzer findings separately. Save visual
review notes against the exact schematic hash; a single clean render is not a
claim about arbitrary future input circuits. For redraws using another writer,
compare both before/after native XML partitions and identity fields in addition
to the intent; do not use this new-project generator as an in-place editor.

## Regression and maintenance

```bash
python3 -m unittest discover -s tests -v
python3 tests/probe_upstream.py --output output/upstream-probe.json
```

The first command uses the standard library; native tests explicitly skip if
KiCad/libraries are unavailable. A skipped native test is not execution evidence.
When `pdftotext` is available, the transform test also checks the actual native
PDF Value bounding boxes for vertical text and mirrored intrusion into bodies.
The optional second command needs the two downloaded `upstream/` repositories
and Node with TypeScript stripping; it executes selected pure source modules
only. Runtime generation needs neither upstream tree nor Node. Add a minimal
fixture for every new real failure, then test the intended observable invariant
and the native output. Pin the changed upstream commit before reusing more code.
