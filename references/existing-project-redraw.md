# Redraw an existing hierarchical project

Use this workflow when the user asks to improve placement and visible wiring
in an existing multi-page KiCad project. It is a procedure for a project-specific
writer and verification, not an automatic multi-page feature of
`build_circuit.py`. For new electrical design or peripheral repairs, also use
[reference-driven-board-design.md](reference-driven-board-design.md).

## Freeze the actual baseline

Save the current editor state before reading files. Inventory the root project,
child sheets, sheet UUID paths, page identifiers, multi-unit instances and local
symbol libraries. Page names need not form a continuous numeric sequence; do
not create a missing number merely to fill a requested range.

Copy the project to a new staging directory and record source hashes. Export
the baseline **root** schematic through native KiCad to XML, raw ERC and PDF.
Keep the complete physical `reference.pin` partitions, including intentional
NC singleton pins, component properties and cross-page interface names. A
per-sheet analyzer can miss hierarchy context and is not connectivity truth.

Define the allowed presentation changes and protected sheets explicitly.
References, component/unit UUIDs, hierarchy, values, MPNs, ratings, footprints,
DNP state and physical pin identity remain unchanged unless the task includes
a separately recorded electrical change. Check named-net dependencies in
netclasses, PCB synchronization and downstream scripts before removing labels.

## Plan complete local circuits

Study full rendered engineering pages and dense details. Record source pages
locally; publish general methods without private PDFs or screenshots.

- Place protection and conditioning along the input-to-output signal path.
  Keep feedback, clock, reset, bias and bypass branches adjacent to their IC
  pins. Make local rail and return connections visible.
- Use a consistent orientation, pitch, passive pattern and field position for
  repeated channels. Keep isolation domains visually separate and identify
  their actual grounds.
- Choose paper size and block grouping by readable functional circuits and
  domain boundaries. Equal component counts across pages are not a target.
- Declare the cross-page and intentional remote labels before routing. Short
  labels directly beside relevant pins are preferable to a detached label wall.
  A failed local route stays a failed candidate; it must not become an implicit
  label connection to pass geometry.

If a presentation symbol is needed, retain a complete comparison of physical
pin number, name, electrical type, hidden state and unit identity. Only drawing
geometry changes. Keep the matching project library and cached symbol coherent;
do not rename or remap physical pins for visual convenience. Coincident pads
are restricted to the same symbol and same net, with each physical pin retained
in the export. See [schematic-generation.md](schematic-generation.md) for the
bounded generator's supported cases.

## Verify the staged candidate

Keep separate results for these checks; no single PASS covers the others.

| Check | Required evidence |
| --- | --- |
| Electrical connectivity | Root native XML has exactly the same physical pin partitions and NC treatment; no missing pins, shorts or splits. |
| Identity and scope | Component properties, unit/UUID context and hierarchy match; protected sheet files are unchanged; library changes are accounted for. |
| Network names | Cross-page names and endpoints remain stable. Preserve local names when they are an interface; if local names legitimately change, record old/new names and the exact pin set and assess downstream dependencies. |
| Native ERC delta | Retain both raw reports. Compare violation type/severity and affected references/pins/messages, accounting for changed coordinates. Investigate each added violation; never rely only on total counts. |
| Geometry and grid | Check serialized bodies, wires, pin legs, fields, labels, anchors, the actual drawing frame and titleblock. Validate connection tips on the native grid, normally 1.27 mm. |
| Render review | Inspect every changed full page and crowded clock/divider/isolation/configuration region through native PDF output. Record each page's review and remaining defects. |

Inherited ERC problems remain disclosed electrical issues. A drawing-only
acceptance can show no new unreviewed ERC regressions while still being
**NOT_RELEASED** as a hardware design. Do not add power flags, exclusions or
change pin types just to lower the count. New-design automated acceptance keeps
the stricter gate described in [schematic-generation.md](schematic-generation.md).

A geometry pass on a 0.635 mm grid can coexist with native off-grid warnings.
Likewise, a model's 4–5 mm page margin may allow content across a 10 mm native
frame. Check the actual native settings and printed frame, including text
outside the symbol body. Do not waive a native finding because a different
geometric model passed.

Render review also catches defects outside collision rules: a reset capacitor
that is electrically joined only through remote labels, a pull-up stem visually
belonging to the previous repeated channel, or pin labels far from the circuit.
Repair those local blocks, then repeat the dependent checks.

## Apply and verify the delivered project

When the user has authorized modification of the original project, apply the
reviewed candidate after checking that the original source hashes still match
the saved baseline. If the user edited the original meanwhile, reconcile those
changes first. Preserve a recoverable backup; do not replace unrelated sheets
or editor state files indiscriminately.

Re-export XML, ERC and PDF from the **final project path**. Verify the delivered
files against the staged manifest and repeat connectivity, identity and ERC
delta checks. Check that library references resolve from that final location.
Where both paths should render identically, compare decoded image dimensions,
mode and pixels; PNG compression or metadata can change file hashes without
changing the drawing.

Deliver the exact changed-page list, final project/PDF, evidence manifest and
remaining electrical limitations. Improving representative pages is not proof
that the whole board has been repaired or qualified for production.
