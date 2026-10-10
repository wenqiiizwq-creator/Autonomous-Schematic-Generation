# Symbol integrity and source-bound circuit contracts

Read this before selecting or repairing symbols, authoring IC peripherals, or
closing a generated board. Keep independent gates for physical pin identity,
symbol artwork, footprint pads, native connectivity, reference peripherals,
functional completeness and operating margins. Passing one cannot close another.

## Establish the active scope and design boundary

Use `audit_project.py` to inventory reachable sheet **instances**, physical
references and selected units. Do not scan historical `.kicad_sch` files as if
they all belonged to the current project. Freeze root/project identity, hashes,
native XML, raw ERC and page list. Inventory every core IC, regulator, op-amp,
comparator, FET/driver and protection device on every active page. Repeated
instances still need package, mode, supply, population and load checks before
reusing a proven part contract.

Derive each feature's boundary from requirements. If discrete AC/DC circuitry
was requested, show the applicable rectification, conversion, magnetics,
sensing, feedback and protection circuits with engineering constraints. If a
qualified module is permitted, its internal circuitry need not be recreated;
required external circuits and integration evidence still apply. More parts or
pages do not by themselves make a design complete. Ordinary IC internal
transistors are not a missing board-level circuit.

Map each required function from source to load with real references, physical
pin endpoints, page locations, assembly states and evidence. Include applicable
sensor/bias/filter, driver/load connector/flyback, RF/matching/antenna, or
energy-storage/conversion/load stages. A named ADC input, MCU GPIO, bus header,
load switch or sheet title cannot stand in for an absent stage. State external
module/load boundaries explicitly. Retaining a logic rail does not prove an
actuator can operate: carry load, energy, time and voltage constraints to the
actual load. Unknown load is not zero load.

## Establish physical pin and source truth

For each exact manufacturer part/package, retain the primary document URL,
revision, file hash and pages/figures actually read. A nearby part's datasheet,
matching filename or available URL does not establish identity. Keep exact MPN
separate from display value and library symbol name.

Map **every physical pin**, including EP/NC and all units, to documented functions.
Check electrical type separately from number/name: a reset output's open-drain
behavior is not proved by a correct pin number. Use explicit reviewed aliases
tied to that part/package; do not strip suffixes or punctuation globally to make
comparisons pass. The XML `+no_connect` marker is separate from electrical type.
Manufacturer function, library type and native wiring are distinct evidence.

Generic family names do not fix a pinout. Before authoring or reusing a symbol for a
discrete part, read the pinning table of the exact orderable MPN: for example the KiCad
library `BCX56` (SOT-89) numbers pins 1=B 2=C 3=E, while Nexperia BCX56-16TX (BCX56T
series) is 1=E 2=C 3=B, so the generic symbol would swap base and emitter. Record the
MPN-bound pin table in the device contract before placing the part.

When footprints are assigned, check footprint pad-number sets, then
independently check manufacturer package drawing, pitch, exposed pad, pad
dimensions and orientation. Matching pad-number sets do not validate mechanical
footprints. At the schematic stage footprints may stay empty; the pin map of the
exact MPN is still required. Missing MPNs, unresolved library paths or
unavailable package drawings remain explicit gaps.

## Detect internal pin-leg faults without moving electrical endpoints

```sh
python3 scripts/audit_symbol_integrity.py path/to/board.kicad_sch \
  --netlist path/to/native.xml --out output/symbol-integrity.json
```

If strict native XML parsing fails, the report retains the source pin, artwork,
hierarchy and coverage diagnostics alongside a failed native axis and XML hash.
Those retained rows do not establish native coverage or qualify a zero-pin
object. Resolve the recorded native error before acceptance.

The command follows actual hierarchy annotations, selects active/common units
and body styles, and compares full physical pin sets with native XML in both
directions. It measures the **inner** end of visible pins against rectangle,
polyline, circle and nondegenerate three-point arc strokes, including half the
stroke width. A body bounding box cannot detect a leg stopping inside a triangle
or outside a sloped edge. Ignoring stroke width falsely flags some normal
capacitor plates. Arc distance follows its sweep, not a full circle.

`CANDIDATE` blocks the graphics gate pending correction or justified disposition;
it does not assert an electrical open. The report records local/sheet tips,
inner coordinates, library hash, unit/style, type, DNP and distance. Hidden pins,
zero-length pins and recognized separate bodyless supply units are
`NOT_APPLICABLE`, with a reason; physical pins still require native coverage.
A single-unit device missing artwork is not a recognized supply unit. Unresolved
inheritance, unsupported artwork preventing attachment determination and
malformed/degenerate geometry are never silently passed. Text/Bezier artwork is
not proof; a pin touching a supported stroke can be checked even when other
unsupported primitives exist. This is not complete raster/text-layout analysis.
The default distance tolerance is 0.16 mm; it does not establish wire connectivity.

The separate `hidden_power` axis rejects physical hidden `power_in`/`power_out`
pins lacking a visible coincident supply anchor with matching type/name and
native connectivity. Graphics `NOT_APPLICABLE` does not close that axis.
Coincident hidden supply copies remain `INSUFFICIENT` under the current bounded
generation contract, even when native XML connects them; do not infer approval
from a shared name or net. Virtual `#` power symbols, visible zero-length pins,
visible separate supply units and hidden passive copies retain their existing
coverage rules. Pin-artwork exceptions cannot bypass this power-visibility check.

For an intentional isolated terminal, retain an explicit disposition:

```json
{"schema_version": 1, "exceptions": [{
  "instance": "/root-uuid/sheet-uuid", "reference": "T1", "unit": 1,
  "pin": "8", "lib_sha256": "<exact lib_sha256 from this audit>",
  "reason": "Documented isolated mechanical terminal; no winding connection",
  "evidence": "project review record and manufacturer drawing locator"
}]}
```

Pass its file with `--exceptions`. There is no blanket NC exemption. An unused
exception, changed library hash or no-longer-applicable candidate fails. An
exception only dispositions a candidate; it cannot close unsupported geometry
or electrical gaps. Generation has no automatic exception bypass: correct the
symbol or use a separately reviewed workflow, retaining failed generation evidence.

For an artwork-only repair, preserve pin **tips**, numbers/types, units,
reference/value/footprint, population and native pin partitions. Change the
internal leg or intended artwork, then re-export and compare. Audit every
instance/cache/project-library copy affected by a shared definition. Refresh
and inspect native detail and full-page views. Do not change wiring or add
power flags merely to clear graphics/ERC candidates.

## Author peripheral expectations independently of the candidate

`verify_reference_contract.py` provides a small explicit format. The complete
[synthetic contract](../tests/fixtures/reference_contract/contract.json) uses a
fictional part/specification solely for testing. It is not a usable circuit.
Author project expectations from requirements and manufacturer sources before
changing/generating the candidate. Copying current connections or pin types into
expected results does not establish correctness.

| Section | Meaning and gate |
| --- | --- |
| `scope.core_refs`, `scope.feature_ids` | Independent lists to cover. Empty scopes are rejected; missing mappings/features are INSUFFICIENT. Reconcile with page inventory and requirements: the tool cannot discover every required function. |
| `sources` | ID maps to `path`, SHA256, primary `url`, `document`, `revision`. Paths resolve relative to the contract, or can be absolute. Changed bytes FAIL; absent files are INSUFFICIENT. Authority and source interpretation still require review. |
| `pin_maps` | Reference maps to exact `identity` (`value`, `mpn`, `footprint`, `lib_id`), source/locator, and complete numbered `pins` with explicit `names`/`types` alias lists. `footprint` may be the empty string at schematic stage, meaning explicitly unassigned; it must still match the native field exactly and is never a wildcard for an assigned footprint. Other identity fields remain nonempty. Uses nonempty native MPN field, otherwise exact native Value; a generic Value is not an MPN substitute. |

Native pin names/types come from the component's exact `libsource` → unique
`libparts/libpart` → unique physical pin number. A node's `pinfunction` can be a
generated identifier such as `STAT_1`; do not strip its suffix or treat it as the
manufacturer pin name. Genuine names such as `Pin_1` remain exact. Missing or
ambiguous library pin metadata is INSUFFICIENT; mismatched names/types and
contradictory native node electrical types remain FAIL. A missing component
identity can independently FAIL even when its metadata has a coverage gap.
Every library physical pin, including unused units, NC and EP, must be in the
contract; omission from both the nodes and contract cannot hide a library pin.
Library pins without a physical number remain a metadata coverage gap.
| `checks` | Unique `id`, `kind`, source/locator. `component` asserts exact value/footprint/library/DNP. `same_net` and `distinct_nets` assert at least two unique `reference.pin` endpoints against native partitions. |
| `features` | Unique ID, boundary, source/locator and nonempty stages. Each stage needs ID, role, real fitted references and check IDs. Missing/DNP required references fail. Review whether the listed references and checks actually implement the stated role. |

```sh
python3 scripts/verify_reference_contract.py path/to/native.xml \
  path/to/reference-contract.json --out output/reference-check.json
python3 scripts/build_circuit.py circuit.json presentation.json \
  --reference-contract path/to/reference-contract.json --output-dir output/new-run
```

The same option exists on `generate_schematic.py`. Symbol integrity automatically
runs inside native verification for both entrypoints and existing reference
builders. A supplied contract must PASS for automated acceptance. Without one,
no source/peripheral claim is made; `datasheet_review: PENDING` remains. For a
board-level IC design, the skill workflow requires a project contract or explicit
uncovered/unsupported findings before calling reference circuits checked.

For a required bypass, check exact capacitor/population, `same_net` for **each**
terminal and intended IC supply/return pin, and `distinct_nets` for supply/return.
Checking only presence, a net name or one terminal misses wrong returns/shorts.
Use physical pin identities; local/hierarchical aliases cannot substitute for
actual connectivity. Numeric values are exact strings in this checker: author
intentional notation or update it explicitly, not silent unit guesses.

Connectivity assertions concern **fitted endpoints on direct native nets**.
The checker does not merge zero-ohm links, traverse internal IC paths, model FET
current flow or validate alternate assemblies. Preserve the all-pads netlist,
then separately audit the fitted DNP/zero-ohm graph and mutually exclusive
configurations. Optional branch wiring and component NC are not IC NC. Record
mode, polarity, default state and active-level reference rails. Qualify
tolerance, effective capacitance, common-mode range, timing, startup/fault/backup
states, thermal and load margins separately.

## Close with negative tests and independent evidence

### Intentional pinless native objects

A mechanical or documentation object may have no physical pins. Preserve its
complete component identity; its pin-integrity result is `NA`, not a part or
manufacturing qualification. Never infer this role from a reference prefix,
library/model name, BOM flag or an empty XML pin list. Electrical parts with
missing exported pins still fail. Unresolved cache inheritance or unavailable
selected-project annotations remains `INSUFFICIENT` and cannot qualify an object.

Use an externally reviewed `source-role-contract.json` with exactly these keys:

```json
{
  "schema_version": 1,
  "project": "board",
  "file_sha256": {"board.kicad_sch": "<complete NativeHierarchy file hash map>"},
  "native_xml_sha256": "<exact reviewed native XML SHA256>",
  "objects": [{
    "reference": "OBJECT1",
    "instance": "/root-uuid/sheet-uuid",
    "symbol_uuid": "object-uuid",
    "lib_id": "Example:Marker",
    "lib_sha256": "<SHA256 of sexpr.dump(cached symbol).encode()>",
    "source_properties": {"Reference": "OBJECT1", "Value": "Marker"},
    "source_flags": {"exclude_from_sim": "yes", "in_bom": "no", "on_board": "yes", "dnp": "unspecified"},
    "role": "mechanical",
    "native_identity": {"value": "Marker", "footprint": "", "datasheet": "", "lib_id": "Example:Marker", "dnp": false, "fields": {}}
  }]
}
```

`source_properties` must contain every source property; the four flags use the
native value or `unspecified` when absent. `role` is only `mechanical` or
`documentation`, selected by an independent source-role review. The checker
verifies exact selected-project reference/instance/UUID, full source and cache
hashes, export identity agreement with source properties, and absence of pins
across every resolved cached unit/style. Native XML additionally must match the
contract hash, descriptor, symbol UUID and sheet path. A stale hash or incorrect
identity fails. No missing annotation may borrow another project's reference.

```sh
python3 scripts/audit_project.py board.kicad_sch --netlist native.xml \
  --source-role-contract source-role-contract.json --out new-hierarchy.json
python3 scripts/audit_symbol_integrity.py board.kicad_sch --netlist native.xml \
  --source-role-contract source-role-contract.json --out new-symbols.json
python3 scripts/verify_schematic.py board.kicad_sch --intent electrical-intent.json \
  --source-role-contract source-role-contract.json --out new-verification
```

The option is forwarded only to hierarchy and symbol audits. It does not waive
ERC, electrical intent, peripheral contracts or electrical-change verification.
`verify_schematic.py` exports a fresh XML: timestamp or other byte changes make an
older XML hash stale and require review/rebinding before symbol qualification.
The read-only Python API is `read_native(xml, source_root=root,
source_roles=contract, project=selected_project)`; without a contract its existing
strict rejection of zero-pin components remains. `native_inventory(xml)` and the
audit reports separately retain XML component/node occurrence counts and the
zero-endpoint list even when strict parsing fails. Those diagnostics neither
qualify a component nor resolve selected-annotation coverage gaps.

Remove a required part, change a value/package, make it DNP, move a return, short
distinct rails and remove a declared stage. Each affected check must reject the
mutation. A source-hash change and wrong pin type must fail even with unchanged
connectivity. Preserve neutral regression cases without proprietary schematics
or manufacturer PDFs in the public skill.

Use native XML as connectivity reference. Before trusting an auxiliary
analyzer's nets, compare complete physical pin partitions, including singleton
and NC pins and assembly state. Resolve divergent aliases/splits or isolate
them as tool gaps. Retain raw ERC/geometry candidates and evidence-based
dispositions. An empty lint report or filtered count is not electrical proof.
Do not merge grounds or add PWR_FLAG to quiet a detector.

Report the gates separately: hierarchy/pages, pin identity/type, artwork,
footprint identity/mechanics, native netlist/ERC, declared peripheral facts,
required functional chains, population variants, calculations and physical
validation. A checker PASS closes only enumerated facts. Missing evidence stays
INSUFFICIENT. Hand full electrical review to `schematic-review` with exact hashes,
sources, findings and remaining conditions; generation does not sign production
release.
