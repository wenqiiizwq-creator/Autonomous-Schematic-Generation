# Human-readable schematic routing

Apply when creating or redrawing circuits, before fixing coordinates. These are
presentation requirements, not changes to the electrical circuit. Electrical
identity, geometry clearance and readability are separate acceptance dimensions.

## 1. Define the reading path before the route

For each functional circuit, record a short presentation plan with:

- The reader's task: follow energy flow, understand feedback, trace a protected
  interface, or identify an IC's required support circuit.
- Actual references/pins belonging to that task, including support components.
- The visible main path and local branches that must remain directly connected.
- Return domains, isolation boundaries, and intentional label-connected endpoints.
- A drawing recipe: straight spine with shunts, controller with local support,
  repeated interface lanes, parallel bank, or another justified arrangement.

A functional block is defined by the relationship it explains. It is not whatever
set of components happens to fit a placement box. Do not declare an IC and each
of its support networks separate blocks solely to permit label-only connections.
Templates describe electrical relationships and pin roles, not fixed reference
numbers or a memorized screenshot. Resolve roles to the actual netlist first.

This plan can be a Markdown table in the project. It is **not** an implemented
extension to Circuit IR or the generator JSON schema.

## 2. Construct the layout from these rules

| ID | Rule and repair action |
| --- | --- |
| HR-01 | Keep a local functional relationship visible. Put an IC's divider, timing, compensation, current-sense filter and associated drive network near the relevant pins and draw their connections. An intentionally separate power unit, dense pin bank, or remote sensing endpoint can use labels when the presentation plan explains the boundary. Do not accept arbitrary label islands as local wiring. |
| HR-02 | Establish the main path first. Use a consistent energy/signal direction within the block; place branches perpendicular to that path where practical. Draw a converter's actual switch/inductor/transformer relationships recognizably. Do not disconnect its central stage into scattered labeled fragments merely to avoid routing. |
| HR-03 | Give parallel elements shared straight rails. Capacitor banks and parallel resistors use aligned terminal rows and regular branch pitch. Reposition or rotate the exceptional component instead of extending the rail into a hook to reach it. Preserve its polarity, value and connectivity. |
| HR-04 | Choose a return representation explicitly. A compact power loop may use a visible return rail; repeated independent shunts may use local, domain-correct ground symbols or short named return connections. Avoid large perimeter ground rectangles and staircase chains through successive channels. Never merge primary, secondary, chassis, signal or Kelvin returns for appearance. |
| HR-05 | Repeat interface lanes consistently. Keep series elements on the lane and shunt protection perpendicular to it. Use the same series/shunt placement pattern in each lane; align repeated devices and order lanes to reduce crossings at the connector. Preserve the real connector pin assignments and any existing paired contacts. |
| HR-06 | Reserve short, direct local paths before routing long inter-block nets. Identify those paths by function (for example drive, sense, feedback and support branches), not alphabetical net order. Visual proximity communicates association; it does not prove short PCB routing or SI/PI performance. |
| HR-07 | Use labels for intentional abstraction. Cross-sheet links, shared supplies and genuine block interfaces are valid uses. Within a directly connected local circuit, omit redundant labels unless they help identify an important node. Avoid decorative label-only branches. Select label scope from actual connectivity; changing global to local is not automatically safe. |
| HR-08 | Place symbols and fields together with their exit corridors. If text forces a simple branch into a detour, move the text within a clear ownership area, adjust the component, or change the block arrangement. Never trade text readability for a shorter wire. Expand the block only when the local arrangement actually needs room. |
| HR-09 | Prefer a few clear bends to wire weaving. Remove avoidable tiny jogs, reversals, enclosing loops and excursions across unrelated blocks. When avoiding one obstacle makes a path obscure, revisit placement or the chosen recipe instead of accepting the first legal route. Do not impose a universal bend count on all topologies. |
| HR-10 | Make connection state unambiguous. Prefer a T branch with a visible junction for a connection; keep nonconnecting orthogonal crossings away from bends, pins and junctions. Rearrange repeated lanes before adding crossings. Do not ban every crossing if the alternative is a worse maze; verify both native connectivity and the rendered distinction. |
| HR-11 | Fit the page to the circuit. Keep a functional group compact enough to read together at the intended viewing/print scale, with whitespace between groups and text large enough to read. Do not spread a small circuit across an A3 page to remove collisions or achieve a page-fill target. |

For a repeated protected interface, the intended pattern is conceptually:

```text
signal A -- R --+---------- connector A
               |
              ESD
               |
          correct return

signal B -- R --+---------- connector B
               |
              ESD
               |
          correct return
```

This is a presentation example, not a protection design. The actual circuit
determines device type, polarity, shared package pins and return topology. A
straight common return rail is also valid when it is clearer and accurately
represents the circuit. A shared multi-channel package may need a different
recipe; do not invent units or split physical pins to imitate this drawing.

### Placement and basic wiring conventions

Apply the following as construction rules, before obstacle routing. **Hard**
constraints preserve connectivity or prevent ambiguous/illegible graphics.
**Defaults** are preferred presentation patterns; adapt them to actual topology,
pin orientation and package structure. Explain exceptions where they impair a
declared reading task. These are schematic conventions, not PCB placement rules.

| Subject | Construction rule | Strength |
| --- | --- | --- |
| IC orientation | Prefer signal inputs on the left, outputs on the right, supply above and return below when the actual symbol supports it. Choose the orientation that clarifies the main function; do not rotate an entire IC merely to shorten one peripheral wire. Bidirectional ports and feedback need their real functional arrangement. | Default |
| IC pin representation | Never change pin numbers, electrical types, mappings or polarity for appearance. A custom symbol may group pins by function only with a separately verified physical pin map; retain units, hidden/stacked pins and identity. | Hard |
| Local support | Place each support network on the side of its associated pin or pin group. A series resistor belongs between the pin and its destination; a shunt capacitor branches off that node to the correct return. Avoid wrapping a local branch around the IC to reach a remote component. | Default |
| Series chains | Align connected terminal centers on one horizontal or vertical axis; place R/L/diodes in the order encountered along the actual path. On a horizontal path, prefer horizontal series elements. Component polarity follows the circuit. | Default |
| Shunts | Prefer vertical capacitors, pull-downs and protection branches below a horizontal path. Put pull-ups toward their supply; show a common node with a short perpendicular branch. Do not turn a shunt into a large decorative loop. | Default |
| Divider/feedback | Stack the upper and lower divider elements vertically, take the midpoint sideways toward the sense/FB pin, and align the lower return. Keep compensation with its actual control nodes; a feedback path may naturally run against the main signal direction. | Default |
| Decoupling | Put the capacitor visibly between the relevant supply and return near the IC's supply group. Multiple capacitors use a compact aligned bank. Large ICs with separate power units can use an explicitly identified decoupling group; do not imply PCB distance from drawing distance. | Default |
| Parallel banks | Align equivalent terminals on common straight rails; keep polarity/orientation and branch spacing consistent. Align terminal centers, not arbitrary body edges. Accommodate different symbol sizes and field widths. | Default |
| Repeated channels | Reuse the same arrangement and spacing. Choose channel order to suit destination pins before routing; never swap electrical pin assignments to reduce crossings. Keep paired signals visually associated. | Default plus hard pin preservation |
| Pin escapes | Leave each pin along its outward direction before the first bend. Reserve a straight exit segment; do not turn at the symbol outline, graze neighboring pin tips, or run over pin names/numbers. | Hard clearance; default escape length |
| Branches and crossings | Use clean T branches with dots for connections. Prefer staggered T branches to an ambiguous four-way intersection. An intentional four-way junction must be unambiguous; a nonconnecting crossing is orthogonal, undotted and separated from endpoints, corners and junctions. Normalize actual branch attachments. | Hard connectivity; default T pattern |
| Route shape | Try straight, L, then Z-shaped connections within the planned corridor. If they fail, reconsider component orientation, row/column position and fields before using more complex paths. These shapes are preferred candidates, not a universal maximum-bend rule. | Default |
| Fields and alignment | Use consistent Reference/Value placement for like-oriented parts: commonly above horizontal parts and beside vertical parts. Reserve their measured extents. Move fields or the block to resolve conflict; never shrink text or allow overlap merely to fit a route. | Hard legibility; default field side |

#### A practical spacing profile

Use a compatible electrical grid `g` (commonly 1.27 mm; 0.635 mm where required
by real pin coordinates). The following is an **initial project drawing profile**,
not an industry standard or implemented generator setting:

- Preferred pin escape before a bend: at least `2g` where the symbol permits.
- Preferred separation of unrelated parallel wire centerlines: at least `2g`.
  Dense native pin fanout may require tighter spacing; inspect it at readable scale.
- For repeated branches, measure the full symbol-plus-field envelope and leave
  about `2g` clear space before the next envelope. Use the widest lane to set a
  consistent pitch, rather than forcing all parts into a fixed body-only pitch.
- Keep functional-group whitespace visibly larger than ordinary intra-group
  spacing; begin with twice the chosen intra-group gap, then adjust to the page.
- Start with the project's readable field size (commonly 1.27 mm); retain that
  scale when comparing layout candidates. Do not derive text clearance from
  grid spacing alone: measure rendered field extents.

These preferred spacings are adjustable; actual no-contact/no-overlap constraints
remain mandatory. Do not snap real terminals off-grid or increase wire length
through unnecessary detours solely to meet a preferred distance.

#### Turn the recipe into explicit relationships

Before assigning final coordinates, record relations such as:

- **Alignment:** series pin endpoints share an axis; bank endpoints share rails.
- **Ordering:** source, series component, branch node and destination follow the
  actual circuit; repeated lanes preserve their chosen order.
- **Association:** a support network occupies the region beside its controlling
  pin group, with a reserved direct connection corridor.
- **Spacing:** repeated pitch includes symbol, field and wire clearances.
- **Routing:** selected nets have fixed spines/branch directions; permitted label
  endpoints and nonconnecting crossings are explicit.

For example, a divider recipe binds `upper resistor`, `lower resistor`, `sense
pin`, `source` and `return` to real parts/pins, then applies vertical alignment
and a sideways midpoint branch. It does not start by assigning unrelated x/y
coordinates and asking A* to discover the divider's shape.

Current scripts do not implement a general solver for these relationships. Keep
them in the presentation plan and translate supported ones into existing layout
parameters; use a scoped writer for the rest. Future checks should examine the
saved positions and wires against these relations, with defaults reported as
review findings and hard violations rejected. A flag saying a template was used
is insufficient.


## 3. Route within a planned structure

Use this construction order:

1. Resolve the recipe to real pins and plan permitted label boundaries.
2. Orient/place the main devices, local support and repeated lanes; reserve
   branch rails, wire corridors and readable fields together.
3. Establish the main spine/rails and important local branches.
4. Route remaining connections within those corridors.
5. Inspect the result. If it breaks the recipe, revise placement/fields/grouping
   and route again. Growing a maze or replacing the failed wire with a label
   does not repair the presentation.

MST pairing minimizes a graph-distance objective; it does not decide which net
should be a rail, which branch should be local, or which path a reader follows.
A* is useful for the remaining constrained paths. Neither algorithm's success
is evidence that the chosen visual topology is good.

Prefer candidates in this order: preserve electrical intent and eliminate
ambiguity/collisions; satisfy the planned reading relationships; reduce unrelated
crossings and unnecessary label searches; then simplify bends, length and page
packing. A shorter total wire length must not override a clearer circuit.

### Current implementation boundary

The low-level generator still expects component placements to be supplied; it
does not choose a topology-specific component layout from the reading recipe.
It supports explicit net groups and the following route controls:

- Net policy: `mode` (`wire`, `labels`, or `power`), `rail_y`, `label`,
  `priority`, `symbol` (for power-symbol mode), `label_kind` (`local` or
  `global`), `label_font_mm`, `label_at`, and `label_hint`.
- Group policy: `pins`, `mode`, `rail_y`, `priority`, and `label_at`.
- `label_at` binds a label terminal to an explicit grid point, outward unit
  direction, and outline side. `label_hint` guides placement of a local label.
- `power` mode requires a real `power:<symbol>` library ID; the native symbol
  carries the net name, and its body and Value field are included as obstacles.

Unspecified wire groups use Manhattan MST; A* considers obstacles and bends.
These route primitives do not automatically enforce HR-01 through HR-11,
recognize the recipes above, or retry a component placement. The optional
readability checker reports geometric diagnostics only; a human still traces
the required reading paths in the rendered drawing. Use supported parameters
or a scoped writer and inspect the serialized output. Do not claim a readability
pass from the router succeeding.

Future automation should compile functional recipes into placement and route
constraints, support retrying placement as well as routes, and inspect the
serialized result independently. A route log is not that independent inspection.

## 4. Accept by tracing the circuit, not by counting artifacts

Read the native-rendered full page and useful detail crops. For every block:

- Follow the declared main path from its real origin to destination.
- For a controller, locate each required local support network and trace its
  connection to the relevant pin and correct return.
- For a bank or repeated interface, compare branch structure and follow one
  lane without confusing it with its neighbor.
- Identify every return domain and isolation crossing, and follow intentional
  label links without ambiguous names or missing destinations.

Record sheet/block, references, the path traced, applicable rule findings and
image/source identity. A checkbox saying "viewed all pages" is insufficient.
Record electrical results separately; neither ERC nor hash freshness establishes
readability. A layout can be electrically unchanged and still fail this review.

Use these **manual review states**, not fabricated tool results:

- `REWORK_REQUIRED`: an applicable rule is violated and the reading task is
  obstructed. Name the path and repair; do not average it away with a score.
- `REVIEW_PENDING`: rendering, object support or path evidence is incomplete.
- `REVIEWED`: all declared reading tasks were inspected without unresolved
  readability findings. This is a bounded reviewer conclusion, not user approval
  or electrical qualification. Later user rejection reopens it.

Label count, bends, wire length, detour ratio and page occupancy are diagnostics.
Do not set universal numerical pass thresholds: a labeled MCU bank and a visible
power stage have different needs. When comparing variants, keep electrical
identity, symbol scale, font size and viewing scale comparable. Do not improve
one metric by hiding relationships or shrinking text.

## 5. Ground future implementation in positive and negative examples

For each recipe being automated, retain an electrically equivalent bad/good
pair with real native schematics and readable renders. Include both the original
failure and a legitimate exception, such as a dense labeled interface or a
necessary crossing. Check native pin partitions and trace the same reading task
in both candidates. Extend to other pin arrangements and component counts before
calling the recipe general. A Markdown rule, successful parser, or collision-free
toy circuit alone does not demonstrate better drawing behavior.
