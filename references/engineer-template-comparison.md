# Comparing an engineer reference and improving a generated schematic

Use an engineer drawing as a presentation reference and a source of candidate
circuit facts. It is not automatically an electrical acceptance certificate.
Keep its image/native files unchanged, preserve the generated baseline, and
make a new revision when values, connections or assembly options change.

## Evidence and scope

Create an extraction ledger with image region, visible reference/value/package,
connection confidence, and unresolved material identity. Distinguish a visible
`330uF/4V` value from an inferred dielectric; neither a capacitor glyph nor a
`C1210` annotation proves a polymer or MLCC part. A current written next to an
inductor does not say whether it is Irms or an Isat rating at a particular drop.
Do not copy pin numbering conventions for exposed pads without the package map.
If only an image is available, do not claim exact source-netlist equivalence.

Compare separately:

- Placement: main energy path, local support groups, feedback loop, array pitch,
  field orientation/association, whitespace, page boundaries and title block.
- Circuit intent: input/output/load target, bias arrangement, enable sequencing,
  mode, soft start, PG voltage, required control networks and assembly options.
- Selection: actual MPN/package, inductance under current/temperature, DCR loss,
  effective capacitance, ESR/ripple ratings, feedback tolerance and protection.

Preserve reasonable differences. More capacitance or a smaller inductor is not
inherently better. Compare benefit, cost and uncertainty before changing it.
Load current and input-capacitor RMS ripple current are different quantities.

## Compact synchronous Buck presentation

The tested TPS53355 example uses an explicit recipe, not a universal automatic
Buck recognizer: `examples/tps53355_compact/`. Its electrical values are a
calculated comparison draft; do not reuse them as qualified defaults.

1. Put VIN and LL physical pin arrays opposite one another. Reorder their graphic
   positions by function while preserving pin numbers, types and all terminals.
2. Use a straight main rail from input to VIN, LL to L, and L to output. Give
   capacitor groups a common power rail and return rail. Reserve pin buses.
3. Place VDD/VREG decoupling beside their pins, configuration above/left, BOOT
   above the LL-to-L segment, and injection/divider below. Keep the compensation
   connections visible; use scoped labels only for explicit remote controls.
4. A regular dense capacitor bank may use 90-degree Reference/Value fields.
   Use consistent orientation and enough pitch for the measured text, body and
   pin exits. Keep full ratings/MPNs as metadata; never delete tolerance merely
   to shorten a visible value. Ordinary fields remain horizontal by default.
5. Specify local group rails where straightness matters. An A* route can be
   electrically valid but visually poor. Inspect native renders after routing,
   including pin-name/number regions and page frame beyond simple AABB checks.
6. Add useful debug provisions only with intent: test points, EN/PG interfaces,
   and optional snubber/bleeder. DNP is an assembly state, not a no-connect pin.
   Record mutually exclusive population rules and external signal requirements.

## Explicit presentation APIs

`generate_schematic.py` and `make_root` accept visible field positions in the
low-level placement JSON (world coordinates, angle 0 or 90, font at least 1 mm):

```json
{"C1":{"at":[50.8,63.5],"fields":{
  "Reference":{"at":[54.61,63.5],"angle":90,"font_mm":1.016},
  "Value":{"at":[56.388,63.5],"angle":90,"font_mm":1.016}
}}}
```

Explicit fields are reserved before automatic fields and routing; collisions
are rejected. This does not add field-style selection to automatic v2 packing.

A net policy can declare groups of real `reference.pin` terminals. Every pin
must appear exactly once. Groups are wired locally and joined using the real
net name; internal group keys never enter the schematic. A group object can
also select `rail_y`, `mode`, or `priority`:

```json
{"VIN_5V":{"groups":[
  {"pins":["J1.1","C1.1","U1.12"],"rail_y":104.14},
  ["U1.19","C9.1"]
]}}
```

Native verification compares the original complete net partitions and label
names. Grouping does not change circuit IR or authorize a labels-only fallback.

## Electrical checks learned from the TPS53355 comparison

Consult the current device datasheet and retain the exact revision. For Rev G:

- RF-open 500 kHz is a nominal continuous-conduction setting. Auto-skip is not
  fixed-frequency operation at light load.
- MODE-to-GND and MODE-to-PGOOD are distinct modes; do not flag a documented
  configuration using a generic pull-down heuristic.
- For ceramic output capacitors use the ripple-injection procedure, including
  `L*Cout/(Rinj*Cinj) > N*Ton/2`, and `N=4` when `L<=250nH`.
- Include injected/output ripple when estimating average VFB and selecting the
  divider. A simple `0.6*(1+Rtop/Rbottom)` estimate can miss the setpoint shift.
- OCP is valley sensed; distinguish average-load trip and instantaneous peak.
  Typical RDS(on), a nominal TRIP equation and an Isat-at-25C curve do not prove
  guaranteed current protection over temperature and process.
- External regulated 5 V bias and an internal VREG supply are different legal
  architectures when the manufacturer allows them. Check voltage headroom
  before copying a series VDD filter at the minimum input voltage.
- Effective capacitance and ESR remain conditional until vendor curves or
  measurements support them. Arithmetic margin is not loop/transient evidence.

Close with native ERC, original-intent pin partition/identity verification,
serialized geometry, full-page/region native renders, an electrical change
ledger, exact hashes, and a list of remaining electrical evidence gaps.

## Peripheral completeness and population evidence

Build two ledgers before simplifying an engineer reference:

- Pin basis: physical number/name, datasheet pin table, relevant application or
  control section, actual connected endpoints, default fitted path, and each
  optional path. Separate manufacturer requirements from calculated values and
  project choices. An IC datasheet and an official manufacturer clarification
  are different sources; retain both when using the latter for a bias choice.
- Peripheral function: mandatory operating network, configuration provision,
  sequencing/status interface, debug/isolation link, local bypass and tuning
  footprint. Each visible branch is retained, changed with a reason, or left
  unresolved; extra series resistors or capacitors do not automatically mean
  the generated design is missing a function.

Never collapse a reference DNP resistor into an IC NC marker when retaining an
engineering adjustment provision is part of the task. Its pads and connections
must exist in the native netlist and BOM, while its default non-conduction is
checked separately. A printed `NC` on a component normally suggests DNP in this
reference context, but the real assembly BOM is needed to confirm production
population. A printed `NC` in the IC pin table is a different instruction.

For TPS53355, Rev G Table 7-1 assigns RF-open to 500 kHz. Both optional RF
resistors may be drawn yet unpopulated. The Rev C example draws 866k to VREG
(650 kHz) and 187k to GND (300 kHz), both DNP by default. A 100k/NC placeholder
in the image is not evidence that a 100k fitted pull-up is a recommended setting.
Preserve the options and annotate their default; do not add a fitted pull-up
solely to make the schematic resemble a reference image.

Audit the populated graph in addition to the native all-pads graph. Remove DNP
parts and collapse only fitted zero-ohm links, then verify open configuration
inputs, mutually exclusive branches, mandatory bias links, external-driver
requirements and paired snubber assembly. A legal RF code must still return
REVIEW_REQUIRED when its frequency changes ripple injection, feedback setpoint,
inductor current, protection and thermal behavior. Do not let engineer approval
or a clean ERC promote such an alternate to a verified converter.

The explicit TPS53355 recipe adds RF/MODE options, PG isolation, separate VDD
and VREG bias links, and VIN/load high-frequency bypasses (37 to 47 physical
components). The 0-ohm VDD link is a test/isolation provision, not an effective
RC filter; copying a 10-ohm filter at a 5 V minimum bias needs a fresh headroom
check. A larger component count alone is never the acceptance criterion.
