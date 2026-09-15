# Expand and repair an existing circuit

Use for authorized electrical changes, including replacement of purchased
modules with concrete board circuits. For presentation-only work use
[existing-project-redraw.md](existing-project-redraw.md); executable checks are
in [project-verification.md](project-verification.md).

## Define the expansion boundary

A purchased AC/DC module can already contain a complete converter. Check its
documented operating limits, derating, isolation, external components and system
requirements before calling its use incomplete. When the user requests discrete
implementation, replace that boundary with actual power-transfer and supporting
circuits. Ordinary ICs do not need their internal transistors drawn. A child
sheet containing real circuits is different from an unimplemented module box.

Inventory every requested page: implemented, changed, optional/DNP or absent.
A connector with named signals does not implement a radio, detector or driver.
Keep unselected devices and missing reference information explicit; do not invent
pin mappings, substitute a similar chip's reference, or assume unknown load is
zero. Continue independent pages while obtaining inputs that constrain others.

## Establish intent before drawing

For every change record exact part/package, source revision and pages read,
external interface pins, power domains, operating states and default population.
Reconcile reference-design conditions with the target. A reference image or
source URL is not a verified electrical model.

- Converters: draw protection/filtering, transfer stage, startup, sensing,
  rectification, feedback/compensation and returns as applicable. Record voltage/
  current stress, low-line operation, tolerance, effective capacitance and
  magnetic limits. Separate calculation, simulation and measurement. Transformer
  test voltage does not establish the system working-insulation rating.
- Processors/storage: verify actual package balls, power, clock, reset, boot and
  unused pins. Count physical pads independently of drawing-unit count. Separate
  hardware population, firmware setup and irreversible device provisioning.
- Bidirectional interfaces: distinguish connector power from IO voltage. Show
  DIR/OE, side-specific bypass/pull-ups, open-drain translation and sequencing.
  Check reset, turnaround and an unpowered side against the actual peripheral.
- Assembly options: DNP components retain wired pads. Declare mutually exclusive
  links and default population. Evaluate the assembled graph with DNP removed
  and fitted zero-ohm links collapsed; the native all-pads graph is insufficient.

Freeze root hierarchy, libraries, component identity, XML, raw ERC and PDF with
hashes. Author new components and complete affected before/after pin partitions
independently of the candidate. Protect unrelated sheets and untouched nets.
Copying expected connectivity from the candidate proves only self-consistency.

## Cross-page symbols and readable local circuits

For multi-unit ICs retain complete physical number/name/type/hidden-state tables;
explicitly review changes in unit ownership. Compose chosen artwork into one
canonical definition and synchronize cached pages with the project library.
Different artwork must not accidentally share one library ID. The published
`symbol_pin_signature()` and `audit_project.py` detect bounded inconsistencies;
they do not automatically repair libraries or establish datasheet correctness.

Place complete branches along physical signal/power flow. Keep geometry and
electrical changes separately recorded. Unsupported hierarchy/global-label or
custom-graphic geometry remains `INSUFFICIENT` until a bounded extension is
tested against native renders. Project-specific bounding-box overrides must not
become universal support silently. This release adds no automatic multi-page
writer and preserves the stock geometry engine's existing coverage boundaries.

## Verify and deliver the exact revision

Keep intended net partitions, identity/assembly, named interfaces, footprint-pad
sets, raw ERC delta, geometry/grid and per-page native render review separate.
Add independent critical-pin contracts and fault cases that break the expected
connection. Keep RF tuning, SI/PI, thermal, insulation/EMC and production tests
separate from schematic checks.

Deliver the current full project/PDF, changed-page ledger, evidence and unresolved
items. Label historical PDFs and partial extracts. Open the new `.kicad_pro` in
the manager as well as its root schematic; another same-named editor may show an
older project. Verify the actual path and hierarchy before claiming the switch.
Publish general methods and neutral fixtures, not private board files, credentials
or restricted manufacturer reference packages.
