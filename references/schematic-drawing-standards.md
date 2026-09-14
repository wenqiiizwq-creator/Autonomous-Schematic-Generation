# Schematic Drawing Standards

Read before creating, adding, editing or redrawing a schematic. The drawing
standard governs readability; datasheets and established intent govern the
electrical circuit. Backend/schema details: [schematic-generation.md](schematic-generation.md).

## 1. Preserve electrical intent

- Keep real MPN, library ID, pin numbers, footprint, values, assembly state and
  net membership independent of placement and routes. Account for NC pins.
- On a redraw, export the baseline native netlist and save the source hash.
  Compare the regenerated native pin partitions and component identity exactly.
  Do not silently change questionable values during a geometry-only redraw.
- Connector pin assignments come from the actual interface, never a drawing
  convention such as “pin 1 must be power”. Do not redesign a symbol's pin
  mapping to make layout easier.

## 2. Select the functional structure

| Topology | Preferred visual structure |
| --- | --- |
| Asynchronous Buck | Input → IC/SW → L → output; visible capacitor branches, catch diode SW-to-GND, local BOOT/feedback/control bands. |
| Synchronous Buck | Same energy-flow structure, using the actual integrated/external switch topology. No invented catch diode. |
| LDO | Input → regulator → output with local input/output capacitors and enable/feedback as present. No SW node or inductor. |
| Integrated-inductor module | Input → module → output. Show external parts actually required by the datasheet. |
| Boost/inverting supply | Follow its real energy path, polarity and return reference; do not force the Buck bus sequence. |
| RC/LC filter, divider | Signal direction is evident; branch/shunt elements visibly terminate at the correct return. |
| Crystal/decoupling | Keep associated IC pins and local support parts in one readable group. |
| MCU/SoC/interfaces | Group by function/power domain; maintain real unit and sheet identities, one cross-sheet net registry and local protection/termination. |

The accepted LM5013 example remains a **Buck-specific reference**: continuous
input-to-output bus, bottom return bus, visible passive branches and an orderly
control band. Apply its readability principles to other blocks without inventing
its circuit structure. These are layout patterns, not verified design templates.

## 3. Place bodies, fields and blocks separately

- Use actual cached/library symbol graphics and active units, including rotation
  and mirror. A fixed-size box or all-units pin envelope is insufficient.
- Keep at least 1.27 mm between bodies where feasible. Account separately for
  wire/pin exit corridors and visible Reference/Value/labels; moving only the
  body does not resolve text collisions.
- Keep ordinary fields horizontal and clearly associated with their component.
  A dense, regular capacitor bank may use consistent 90-degree Reference/Value
  fields with measured pitch and native visual verification; see
  [engineer-template-comparison.md](engineer-template-comparison.md). Reserve
  text space before routing. Prefer a clear side; if none exists, expand or move
  the block instead of returning the least-overlapping position as success.
- Keep input/output direction apparent. Separate functional blocks with clear
  space; avoid interleaving unrelated control parts or scattering support parts.
- Reserve page frame, title, notes and other keepouts. Review whole-page
  allocation as well as crowded regions. A sparse small test block does not
  establish good packing for a multi-block product schematic.

## 4. Wiring and label policy

- Use orthogonal wires on a grid compatible with actual pin positions
  (usually 1.27 mm; some symbols require 0.635 mm). Do not silently snap pins.
- Wires must avoid body graphics, visible text and other nets' terminal/route
  corridors. Pin direction constrains how a wire leaves the component.
- Prefer visible local connections. Use named rails and labels where meaningful;
  remote labels are an explicit intent/layout choice, not a silent fallback
  when routing fails. Do not label every local wire automatically.
- Scope block-local names (`SW_5V`, `FB_5V`, etc.) so unrelated blocks cannot
  short through reused labels. Label-connected islands must use the exact same
  net name and scope.
- Split rails at branches and contacts; merge duplicate collinear same-net
  segments and preserve attachment points. Add dots for real multiway
  junctions, not every corner. Different-net overlap/contact is a defect.
- Label anchors belong on the correct wire/pin. Check field justification and
  text extents after writing, including native rotation behavior.
- Add PWR_FLAG only where a justified source drives a power net. Its geometry
  does not establish source capability; verify native ERC and the actual power
  topology. Avoid gratuitous flags used to suppress real errors.

### Version-specific connectivity facts

Native KiCad XML is the authority. The current regression suite tests unnamed
direct pin-to-pin wires and an unsplit T with an explicit junction on the locally
installed KiCad version. On **10.0.4** these are connected as expected. Therefore:

- Do not claim that a single wire between pins or an unnamed net is always
  dropped. Those earlier skill statements were overgeneralized.
- Explicit branch splitting remains the writer's normalization convention, not
  proof that every unsplit branch is illegal in every KiCad.
- Coincident pin tips and legacy KiCad versions need their own native probes;
  do not infer behavior from appearance. The bounded generator rejects
  coincident terminals instead of silently selecting a connectivity policy.

## 5. Mandatory verification gate

1. Native ERC: no unresolved errors/warnings. Keep the full report, exclusions,
   ignored-check metadata, command result and exact KiCad version. An explained
   residual warning is still a residual warning, not “0/0”.
2. Native XML netlist: all intended `reference.pin` partitions match exactly;
   no unintended shorts, opens, lost pins or component identity changes. Use
   source-to-output comparison too for a redraw.
3. Geometry: explicitly account for body overlap, wire-through-body, all visible
   field/label collisions (including same-owner), wire/text and pin/text overlap,
   page/title intrusion, electrical grid, wire/label/NC/junction attachment and
   cross-net contact. Report unsupported objects as coverage gaps.
4. Existing analyzer: reconcile findings and heuristics with datasheet truth,
   including regulator Vref/formulas. Analyzer counts alone are not proof.
5. Native PDF/PNG: inspect the full page and crowded regions. Confirm text
   direction, legibility, pin names/numbers, association, local paths and page
   composition. Geometry uses approximate text boxes and conservative arcs.
6. Electrical evidence: pinout/package, ratings, values and required networks
   meet the design intent and datasheet. A geometry fixture is not a qualified
   electrical design.

`AUTOMATED_PASS` only covers automated gates; visual and datasheet reviews
remain pending. Do not report completion from ERC alone, analyzer JSON alone,
API success or a solver's `solved` flag.

## 6. Repair, rerun and handoff

Keep exact failing inputs and findings, adjust the relevant layout block, and
regenerate into a new output directory. Repeat affected native/geometry/render
checks after edits. Do not make untracked coordinate patches bypassing intent.

For EasyEDA Pro, hand off to `easyeda-schematic-draw` with the same electrical
mapping and readability criteria. For unsupported native KiCad authoring, use
a scoped project writer; preserve multi-unit/hierarchy information and apply
the same gates instead of flattening the input.
